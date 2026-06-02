import { useParams, Outlet, useNavigate } from 'react-router-dom'
import { Tabs, Button } from 'antd'
import { ArrowLeftOutlined } from '@ant-design/icons'

export default function ProjectDetail() {
  const { projectId } = useParams()
  const navigate = useNavigate()

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Button
          type="link"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/projects')}
        >
          返回项目列表
        </Button>
      </div>
      <Tabs
        defaultActiveKey="architecture"
        items={[
          {
            key: 'architecture',
            label: '架构图',
            children: <Outlet />,
          },
        ]}
      />
    </div>
  )
}
