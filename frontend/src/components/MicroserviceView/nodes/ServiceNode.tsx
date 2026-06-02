import { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { Card, Badge, Tag } from 'antd'

interface ServiceNodeData {
  label: string
  status?: string
  endpointCount?: number
}

function ServiceNode({ data, selected }: NodeProps<ServiceNodeData>) {
  const statusColors = {
    healthy: 'success',
    degraded: 'warning',
    unhealthy: 'error',
  }
  
  const statusColor = statusColors[data.status as keyof typeof statusColors] || 'success'
  
  return (
    <>
      <Handle type="target" position={Position.Top} />
      <Badge status={statusColor as any} text={data.label}>
        <Card
          size="small"
          style={{
            minWidth: 120,
            backgroundColor: selected ? '#e6f7ff' : 'white',
            borderColor: selected ? '#1890ff' : '#d9d9d9',
          }}
        >
          <div style={{ fontWeight: 500, marginBottom: 4 }}>{data.label}</div>
          <div style={{ fontSize: 12, color: '#666' }}>
            <Tag color="blue">{data.endpointCount || 0} 个端点</Tag>
          </div>
        </Card>
      </Badge>
      <Handle type="source" position={Position.Bottom} />
    </>
  )
}

export default memo(ServiceNode)
