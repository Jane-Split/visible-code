import ExecutionAnimation from './index'

// 模拟执行步骤
const demoSteps = [
  {
    order: 0,
    line: 1,
    action: 'assign',
    description: '初始化变量 name = "World"',
    variables: { name: { type: 'String', value: '"World"' } },
    callStack: ['main()'],
  },
  {
    order: 1,
    line: 3,
    action: 'call',
    description: '调用 greet(name)',
    variables: { name: { type: 'String', value: '"World"' } },
    callStack: ['main()', 'greet(name)'],
  },
  {
    order: 2,
    line: 5,
    action: 'assign',
    description: '拼接字符串 message = "Hello, " + name',
    variables: {
      name: { type: 'String', value: '"World"' },
      message: { type: 'String', value: '"Hello, World"' },
    },
    callStack: ['main()', 'greet(name)'],
  },
  {
    order: 3,
    line: 7,
    action: 'branch',
    description: '判断 message 长度 > 0',
    variables: {
      name: { type: 'String', value: '"World"' },
      message: { type: 'String', value: '"Hello, World"' },
    },
    callStack: ['main()', 'greet(name)'],
  },
  {
    order: 4,
    line: 8,
    action: 'call',
    description: '调用 print(message)',
    variables: { message: { type: 'String', value: '"Hello, World"' } },
    callStack: ['main()', 'greet(name)', 'print(message)'],
  },
  {
    order: 5,
    line: 9,
    action: 'return',
    description: 'greet 方法返回 message',
    variables: { message: { type: 'String', value: '"Hello, World"' } },
    callStack: ['main()', 'greet(name)'],
  },
  {
    order: 6,
    line: 4,
    action: 'return',
    description: 'main 方法结束',
    variables: { message: { type: 'String', value: '"Hello, World"' } },
    callStack: ['main()'],
  },
]

export function ExecutionAnimationDemo() {
  const handleStepChange = (step: any) => {
    console.log('当前步骤:', step)
    // 可以在这里联动 Monaco Editor
  }

  return (
    <ExecutionAnimation
      steps={demoSteps}
      onStepChange={handleStepChange}
    />
  )
}

export { demoSteps }
