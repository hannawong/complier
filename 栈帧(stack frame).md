#### 栈帧(stack frame)

每次调用和执行一个函数，都会在栈空间上开辟一片空间，这篇空间就叫“栈帧”。栈帧里存放了执行这个函数需要的各种数据，包括局部变量、callee-save 寄存器等等

栈帧分为三块：

1. 栈顶是计算表达式用的运算栈，它可能为空（当前不在计算某表达式的过程中）
2. 然后一片空间存放的是当前可用的所有局部变量
3. 返回地址、老的栈帧基址等信息

sp: 栈顶指针 fp:栈帧基址

![1607577045852](C:\Users\zh-wa\AppData\Roaming\Typora\typora-user-images\1607577148450.png)

![1607577232310](C:\Users\zh-wa\AppData\Roaming\Typora\typora-user-images\1607577232310.png)

- 性质1：

  每条语句开始执行和执行完成时，汇编栈帧大小都等于8+4\*局部变量个数个字节，其中4==sizeof(int)是一个int变量占的字节数(运算栈为空，return address 和old fp各占4个字节)

- 性质2：

  汇编栈帧底部还保存了 `fp` 和返回地址，使得函数执行完成后能够返回 caller 继续执行。

把栈帧设计成这样，访问变量就可以直接用 `fp` 加上偏移量来完成。 例如第 1. 小图中，“读取 a” 就是加载 `-12(fp)`；第 3. 小图中，“保存到 c” 就是保存到 `-20(fp)`。

#### 建立栈帧

进入一个函数后，在开始执行函数体语句的汇编之前，要做的第一件事是：建立栈帧。 每个函数最开始、由编译器生成的用于建立栈帧的那段汇编被称为函数的 **prologue**。

举个例子，下面是一种可能的 prologue 写法。 其中 `FRAMESIZE` 是一个编译期已知的常量，等于 `8 + 4 * 局部变量个数`（这名字不太准确，因为有运算栈，栈帧大小其实不是常量）

```assembly
    addi sp, sp, -FRAMESIZE         # 分配空间
    sw ra, FRAMESIZE-4(sp)          # 储存返回地址
    sw fp, FRAMESIZE-8(sp)          # 储存 fp
    addi fp, sp, FRAMESIZE          # 更新 fp
```

当然，开始执行函数时需要建立栈帧，结束执行时就需要销毁栈帧。 函数末尾、用于销毁栈帧的一段汇编叫函数的 **epilogue**，它要做的是：

1. 设置返回值
2. 回收栈帧空间
3. 恢复 `fp`，跳回返回地址（`ret` 就是 `jr ra`）

把返回值放在栈顶的话，下面是 epilogue 一种可能的写法。

> 前缀 `FUNCNAME` 是当前函数函数名，例如 `main`，加上前缀以区分不同函数的 epilogue。
>
> ```
> FUNCNAME_epilogue:                  # epilogue 标号，可作为跳转目的地
>     lw a0, 0(sp)                    # 从栈顶加载返回值，此时 sp = fp - FRAMESIZE - 4(例子中的栈顶的36)
>     addi sp, sp, 4                  # 弹出栈顶的返回值
>     lw fp, FRAMESIZE-8(sp)          # 恢复 fp
>     lw ra, FRAMESIZE-4(sp)          # 恢复 ra
>     addi sp, sp, FRAMESIZE          # 回收空间
>     jr ra                           # 跳回 caller
> ```
>
> 就 step5，保存恢复 fp/ra 的确不必要。但是加上会让后面步骤更方便。

##### 实验内容

IR:

| 指令        | 参数                 | 含义                                                         | IR 栈大小变化 |
| ----------- | -------------------- | ------------------------------------------------------------ | ------------- |
| `frameaddr` | 一个非负整数常数 `k` | 把当前栈帧底下开始第 `k` 个元素的**地址**压入栈中            | 增加 1        |
| `load`      | 无参数               | 将栈顶弹出，作为地址 [1](https://decaf-lang.github.io/minidecaf-tutorial/docs/lab5/guide.html#fn_1) 然后加载该地址的元素（`int`），把加载到的值压入栈中 | 不变          |
| `store`     | 无参数               | 弹出栈顶作为地址，读取新栈顶作为值，将值写入地址开始的 `int` | 减少 1        |
| `pop`       | 无参数               | 弹出栈顶，忽略得到的值                                       | 减少 1        |

例如 `int main(){int a=2; a=a+3; return a;}`，显然 `a` 是第 0 个变量。 那它的 IR 指令序列是（每行对应一条语句）：

```
push 2 ; frameaddr 0 ; store ; pop ;
frameaddr 0 ; load ; push 3 ; add ; frameaddr 0 ; store ; pop ;
frameaddr 0 ; load ; ret ;
```

IR 对应汇编：

- frameaddr k: 

  ```
  addi sp, sp, -4 ;  #开辟运算栈空间
  addi t1, fp, -12-4*k ; #获取第k个元素的*地址*
  sw t1, 0(sp) ##把第k个元素的地址存到新开辟的运算栈空间中。
  ```

- load:

  ```
  lw t1, 0(sp) ; ##获取栈顶的值，这是个地址
  lw t1, 0(t1) ; ##加载地址中的元素
  sw t1, 0(sp) ##保存在栈中
  ```

- store:

  ```
  lw t1, 4(sp) ; ##读取次栈顶(int)
  lw t2, 0(sp) ; ##读取栈顶(一个地址)
  addi sp, sp, 4 ;
  sw t1, 0(t2) ##把次栈顶的值存到栈顶
  ```

- ret：

  ```
  
  ```
