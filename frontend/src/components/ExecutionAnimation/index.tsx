import { useState, useEffect, useCallback, useRef } from 'react'
import { Card, Button, Space, Slider, Table, Tag, Tooltip, Select } from 'antd'
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  StepForwardOutlined,
  StepBackwardOutlined,
  ReloadOutlined,
  FastForwardOutlined,
} from '@ant-design/icons'

export interface ExecutionStep {
  order: number
  line: number
  action: string          // 'assign' | 'call' | 'return' | 'branch' | 'loop'
  description: string    // 步骤描述
  variables?: Record<string, { type: string; value: string }>
  callStack?: string[]
  highlightRange?: { start: number; end: number }
}

interface ExecutionAnimationProps {
  steps: ExecutionStep[]
  onStepChange?: (step: ExecutionStep) => void
  code?: string
}

export default function ExecutionAnimation({
  steps,
  onStepChange,
  code,
}: ExecutionAnimationProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const currentStepData = steps[currentStep] || null

  // 播放/暂停
  const togglePlay = useCallback(() => {
    setIsPlaying(!isPlaying)
  }, [isPlaying])

  // 步进
  const stepForward = useCallback(() => {
    if (currentStep < steps.length - 1) {
      const next = currentStep + 1
      setCurrentStep(next)
      onStepChange?.(steps[next])
    } else {
      setIsPlaying(false)
    }
  }, [currentStep, steps, onStepChange])

  const stepBackward = useCallback(() => {
    if (currentStep > 0) {
      const prev = currentStep - 1
      setCurrentStep(prev)
      onStepChange?.(steps[prev])
    }
  }, [currentStep, steps, onStepChange])

  // 重置
  const reset = useCallback(() => {
    setIsPlaying(false)
    setCurrentStep(0)
    onStepChange?.(steps[0])
  }, [steps, onStepChange])

  // 自动播放
  useEffect(() => {
    if (isPlaying) {
      timerRef.current = setInterval(() => {
        stepForward()
      }, 1000 / speed)
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [isPlaying, speed, stepForward])

  // 进度条拖拽
  const handleProgressChange = (value: number) => {
    setCurrentStep(value)
    onStepChange?.(steps[value])
  }

  // 动作颜色
  const actionColors: Record<string, string> = {
    assign: 'blue',
    call: 'purple',
    return: 'green',
    branch: 'orange',
    loop: 'cyan',
  }

  // 变量表格列
  const variableColumns = [
    { title: '变量名', dataIndex: 'name', key: 'name', width: 100 },
    { title: '类型', dataIndex: 'type', key: 'type', width: 100 },
    { title: '值', dataIndex: 'value', key: 'value' },
  ]

  const variables = currentStepData?.variables
    ? Object.entries(currentStepData.variables).map(([name, info]) => ({
        key: name,
        name,
        type: info.type,
        value: info.value,
      }))
    : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* 控制栏 */}
      <Card size="small">
        <Space direction="vertical" style={{ width: '100%' }}>
          <Space>
            <Tooltip title="上一步">
              <Button icon={<StepBackwardOutlined />} onClick={stepBackward} disabled={currentStep === 0} />
            </Tooltip>
            <Tooltip title={isPlaying ? '暂停' : '播放'}>
              <Button type="primary" icon={isPlaying ? <PauseCircleOutlined /> : <PlayCircleOutlined />} onClick={togglePlay} />
            </Tooltip>
            <Tooltip title="下一步">
              <Button icon={<StepForwardOutlined />} onClick={stepForward} disabled={currentStep === steps.length - 1} />
            </Tooltip>
            <Tooltip title="重置">
              <Button icon={<ReloadOutlined />} onClick={reset} />
            </Tooltip>
            <span style={{ marginLeft: 16 }}>
              步骤 {currentStep + 1} / {steps.length}
            </span>
          </Space>
          <Space>
            <span>速度:</span>
            <Select
              value={speed}
              onChange={setSpeed}
              style={{ width: 80 }}
              options={[
                { value: 0.5, label: '0.5x' },
                { value: 1, label: '1x' },
                { value: 2, label: '2x' },
                { value: 4, label: '4x' },
              ]}
            />
          </Space>
          <Slider
            min={0}
            max={steps.length - 1}
            value={currentStep}
            onChange={handleProgressChange}
            tooltip={{ formatter: (v) => `步骤 ${Number(v) + 1}` }}
          />
        </Space>
      </Card>

      {/* 主内容区 */}
      <div style={{ display: 'flex', gap: 12 }}>
        {/* 步骤列表 */}
        <Card size="small" title="执行步骤" style={{ flex: 1, maxHeight: 400, overflow: 'auto' }}>
          {steps.map((step, index) => (
            <div
              key={step.order}
              onClick={() => {
                setCurrentStep(index)
                onStepChange?.(step)
              }}
              style={{
                padding: '6px 12px',
                cursor: 'pointer',
                backgroundColor: index === currentStep ? '#e6f7ff' : index < currentStep ? '#f6ffed' : 'transparent',
                borderLeft: index === currentStep ? '3px solid #1890ff' : '3px solid transparent',
                marginBottom: 2,
                display: 'flex',
                alignItems: 'center',
                gap: 8,
              }}
            >
              <span style={{ color: '#999', fontSize: 12, width: 24 }}>#{step.order + 1}</span>
              <Tag color={actionColors[step.action] || 'default'} style={{ margin: 0 }}>
                {step.action}
              </Tag>
              <span style={{ fontSize: 13 }}>
                行 {step.line}: {step.description}
              </span>
            </div>
          ))}
        </Card>

        {/* 右侧面板 */}
        <div style={{ width: 300, display: 'flex', flexDirection: 'column', gap: 12 }}>
          {/* 变量状态 */}
          <Card size="small" title="变量状态">
            {variables.length > 0 ? (
              <Table
                size="small"
                dataSource={variables}
                columns={variableColumns}
                pagination={false}
                scroll={{ y: 150 }}
              />
            ) : (
              <div style={{ color: '#999', textAlign: 'center', padding: 20 }}>暂无变量</div>
            )}
          </Card>

          {/* 调用栈 */}
          <Card size="small" title="调用栈">
            {currentStepData?.callStack && currentStepData.callStack.length > 0 ? (
              <div>
                {currentStepData.callStack.map((frame, i) => (
                  <div
                    key={i}
                    style={{
                      padding: '4px 8px',
                      backgroundColor: i === (currentStepData.callStack?.length || 0) - 1 ? '#e6f7ff' : '#f5f5f5',
                      marginBottom: 2,
                      fontSize: 12,
                      borderLeft: i === (currentStepData.callStack?.length || 0) - 1 ? '2px solid #1890ff' : '2px solid transparent',
                    }}
                  >
                    {i === 0 ? '▶' : '  '} {frame}
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ color: '#999', textAlign: 'center', padding: 20 }}>调用栈为空</div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
