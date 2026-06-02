import { useParams, useNavigate } from 'react-router-dom'
import { Card, Row, Col, Statistic, Button, Space, message, Descriptions, Spin } from 'antd'
import {
  ArrowLeftOutlined,
  ApartmentOutlined,
  NodeIndexOutlined,
  BranchesOutlined,
  BarChartOutlined,
} from '@ant-design/icons'
import { useState, useEffect } from 'react'
import api from '../services/api'

interface Project {
  id: number
  name: string
  repository_url: string
  language: string
  status: string
  created_at: string
  node_count: number
  edge_count: number
  module_count: number
  class_count: number
  method_count: number
}

export default function ProjectDetail() {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const [project, setProject] = useState<Project | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (projectId) {
      fetchProject()
    }
  }, [projectId])

  const fetchProject = async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const response = await api.get(`/projects/${projectId}`)
      setProject(response.data)
    } catch (error) {
      message.error('获取项目详情失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: 100 }}>
        <Spin size="large" tip="加载中..." />
      </div>
    )
  }

  if (!project) {
    return <Card>项目不存在</Card>
  }

  return (
    <div>
      <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/projects')} style={{ marginBottom: 16 }}>
        返回列表
      </Button>

      <Card title="项目概览" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="项目名称">{project.name}</Descriptions.Item>
          <Descriptions.Item label="编程语言">{project.language}</Descriptions.Item>
          <Descriptions.Item label="仓库地址" span={2}>
            {project.repository_url}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">{project.created_at}</Descriptions.Item>
          <Descriptions.Item label="状态">{project.status}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="模块数"
              value={project.module_count || 0}
              prefix={<ApartmentOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="类/接口数"
              value={project.class_count || 0}
              prefix={<NodeIndexOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="方法数"
              value={project.method_count || 0}
              prefix={<BranchesOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="依赖边数"
              value={project.edge_count || 0}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card title="可视化视图">
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <Button
            type="primary"
            size="large"
            icon={<ApartmentOutlined />}
            onClick={() => navigate(`/projects/${projectId}/architecture`)}
          >
            架构图视图
          </Button>
        </Space>
      </Card>
    </div>
  )
}
