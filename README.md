# 这是什么？

这是一个使用python编写的，简单的测试工具，用于实现批量的安卓（不仅仅是安卓）指令的配置并执行。

当然，这只是一个简单的框架，我们可以为其编写一定的界面，使其变得更加实用且美观。

# 使用方法

## 配置commend.yml文件

```yaml
# exp为输入指令的名称
exp:
# describe为指令的描述，输入 Etool help可以打印commend.yml中的所有命令
    describe: It's a test cmd
# 指令支持Windows和Linux，并且二者共用同一条指令，如果不同，则三个参数都需要分开写
    Windows:
    Linux:
# 指令，指令支持两种形式：
  # str格式：如：./script/getlog.py ./，ls -a，目前支持调用python脚本和使用系统cmd的相关内容
  # list格式：如：[$1,uf,$2],其中$开头的是可以通过工具传入的参数，最后经过处理，会合成一条str的指令，即"$1 uf $2"
        cmd: ./script/getlog.py ./
# threshold，捕获关键字，目前支持以下四种形式：
  # py`python语句`：可以以"result = data.xxx"等任何你能想到的python代码形式进行编写，其中result和data两个参数不能变即可，data为传入的参数，result的传出的结果
  # re`正则语句`
  # 全词匹配：即在threshold后填入str，捕获到的log中必须包含该str才认定为True
  # 上下限：使用[1,3]这样的形式，传入数据须经过处理，成为int型才可以传入
        threshold: 
  # timeout：超时时间，不填则为99999秒，当到达设定的超时时间，就会return Etool timeout异常
        timeout: 
```

## 配置config.yml文件

该文件目前仅两个参数：

savelog: false 是否保存log，不保存仅会在终端打印

logname: default log名称，default则为以当此运行时间为名称

# 相关方法

## exec(action,argv)

action：commend.yml中配置的命令名称

argv：命令参数，没有可不填

## send(cmd,TX=None)

cmd：exec方法执行完成，会return一个cmd str，填入该cmd str

TX：如果不想使用系统cmd，可以把其他（如串口）的发送方法填入这里

## result(execRes)

execRes：send方法执行完成，return的值，如果需要修饰或使用了TX，请自定义修饰函数后，将修饰过的str传入

## isValid(data)

data：将上述方法的返回值填入data，如果返回值合法，则继续执行，否者raise相应错误

## help()

打印commend.yml中所有命令
