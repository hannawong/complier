#### if 语句和条件表达式

IR：

显然，我们需要跳转指令以实现 if，同时还需要作为跳转目的地的标号（label）。 我们的跳转指令和汇编中的类似，不限制跳转方向，往前往后都允许。

| 指令    | 参数       | 含义                                                         | IR 栈大小变化 |
| ------- | ---------- | ------------------------------------------------------------ | ------------- |
| `label` | 一个字符串 | 什么也不做，仅标记一个跳转目的地，用参数字符串标识           | 不变          |
| `beqz`  | 同上       | 弹出栈顶元素，如果它等于零，那么跳转到参数标识的 `label` 开始执行(branch equal zero) | 减少 1        |
| `bnez`  | 同上       | 弹出栈顶元素，如果它不等于零，那么跳转到参数标识的 `label` 开始执行(branch not equal zero) | 减少 1        |
| `br`    | 同上       | 无条件跳转到参数标识的 `label` 开始执行                      | 不变          |

注意一个程序中的标号，也就是 `label` 的参数，必须唯一，否则跳转目的地就不唯一了。 简单地维护一个计数器即可，例如 `label l1`, `label l2`, `label l3` ...

Visitor 遍历 AST 遇到一个有 else 的 if 语句，为了生成其 IR，要生成的是

1. 首先是 `条件表达式的 IR`：计算条件表达式。
2. `beqz ELSE_LABEL`：判断条件，若条件不成立则执行 else 子句（跳转到5）
3. 跳转没有执行，说明条件成立，所以之后是 `then 子句的 IR`
4. `br END_LABEL`：条件成立，执行完 then 以后就结束了
5. `label ELSE_LABEL`，然后是 `else 子句的 IR`
6. `label END_LABEL`：if 语句结束。

> 例子：`if (a) return 2; else a=2+3;` 的 IR 是
>
> 1. `frameaddr k ; load`，其中 `k` 是 `a` 的 frameaddr
> 2. `beqz else_label1`，数字后缀是避免标号重复的
> 3. `push 2 ; ret`
> 4. `br end_label1`
> 5. `label else_label1`，然后是 `push 2 ; push 3 ; add ; frameaddr k ; store ; pop`
> 6. `label end_label1`

##### 汇编生成：

| IR                | 汇编                                                         |
| ----------------- | ------------------------------------------------------------ |
| `label LABEL_STR` | `LABEL_STR:`                                                 |
| `br LABEL_STR`    | `j LABEL_STR`[2](https://decaf-lang.github.io/minidecaf-tutorial/docs/lab6/guide.html#fn_2) |
| `beqz LABEL_STR`  | `lw t1, 0(sp) ; addi sp, sp, 4 ; beqz t1, LABEL_STR`         |
| `bnez LABEL_STR`  | `lw t1, 0(sp) ; addi sp, sp, 4 ; bnez t1, LABEL_STR`         |

