import { Handle, Position, NodeProps } from 'reactflow'
import { Tag } from 'antd'

interface MethodNodeData {
  label: string
  type: string
  qualifiedName?: string
  modifiers?: string[]
  signature?: string
}

export default function MethodNode({ data, selected }: NodeProps<MethodNodeData>) {
  return (
    <>
      <Handle type="target" position={Position.Top} />
      <div
        style={{
          padding: '4px 8px',
          backgroundColor: selected ? '#e6f7ff' : '#fafafa',
          border: `1px solid ${selected ? '#1890ff' : '#d9d9d9'}`,
          borderRadius: 4,
          fontSize: 12,
        }}
      >
        <Tag color="green" style={{ marginRight: 4 }}>
          {data.type === 'method' ? 'M' : 'F'}
        </Tag>
        {data.label}
      </div>
      <Handle type="source" position={Position.Bottom} />
    </>
  )
}
