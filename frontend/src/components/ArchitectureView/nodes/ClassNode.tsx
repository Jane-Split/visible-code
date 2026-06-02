import { Handle, Position, NodeProps } from 'reactflow'
import { Card, Tag, Tooltip } from 'antd'

interface ClassNodeData {
  label: string
  type: string
  qualifiedName?: string
  filePath?: string
  modifiers?: string[]
  annotations?: string[]
}

export default function ClassNode({ data, selected }: NodeProps<ClassNodeData>) {
  const typeColor = {
    class: '#volcano',
    interface: '#geekblue',
    enum: '#purple',
  }[data.type] || '#geekblue'

  return (
    <>
      <Handle type="target" position={Position.Top} />
      <Tooltip title={data.qualifiedName}>
        <Card
          size="small"
          style={{
            minWidth: 120,
            backgroundColor: selected ? '#e6f7ff' : 'white',
            borderColor: selected ? '#1890ff' : typeColor,
            borderLeft: `3px solid ${typeColor}`,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <Tag color={typeColor} style={{ margin: 0, fontSize: 10 }}>
              {data.type}
            </Tag>
            <span style={{ fontWeight: 500 }}>{data.label}</span>
          </div>
          {data.modifiers && data.modifiers.length > 0 && (
            <div style={{ fontSize: 10, color: '#888', marginTop: 4 }}>
              {data.modifiers.slice(0, 2).join(' ')}
            </div>
          )}
        </Card>
      </Tooltip>
      <Handle type="source" position={Position.Bottom} />
    </>
  )
}
