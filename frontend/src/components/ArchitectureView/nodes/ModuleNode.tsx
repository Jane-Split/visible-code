import { Handle, Position, NodeProps } from 'reactflow'
import { Card, Tag } from 'antd'

interface ModuleNodeData {
  label: string
  type: string
  qualifiedName?: string
  filePath?: string
  modifiers?: string[]
  annotations?: string[]
}

export default function ModuleNode({ data, selected }: NodeProps<ModuleNodeData>) {
  return (
    <>
      <Handle type="source" position={Position.Bottom} />
      <Handle type="target" position={Position.Top} />
      <Card
        size="small"
        style={{
          minWidth: 150,
          backgroundColor: selected ? '#e6f7ff' : '#f0f5ff',
          borderColor: selected ? '#1890ff' : '#d9d9d9',
        }}
      >
        <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
          {data.annotations?.map((ann) => (
            <Tag key={ann} color="blue" style={{ fontSize: 10 }}>
              @{ann}
            </Tag>
          ))}
          {data.label}
        </div>
        <div style={{ fontSize: 11, color: '#666' }}>
          {data.modifiers?.join(' ')}
        </div>
      </Card>
    </>
  )
}
