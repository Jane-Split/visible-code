import { useState, useEffect, useRef } from 'react'
import { Table, Button, Space, Modal, Form, Input, Select, message, Popconfirm, Badge } from 'antd'
import { PlusOutlined, DeleteOutlined, SyncOutlined, EyeOutlined } from '@ant-design/icons'
import api from '../../services/api'

interface Project {
  id: string
  name: string
  source_type: 'git' | 'local'
  source_url: string
  current_branch?: string
  status: string
  created_at: string
}

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    fetchProjects()
    // 开始轮询
    startPolling()
    return () => stopPolling()
  }, [])

  let currentIntervalMs = 3000 // 初始3秒

  const startPolling = (intervalMs = 3000) => {
    stopPolling()
    currentIntervalMs = intervalMs
    pollingIntervalRef.current = setInterval(() => {
      fetchProjects(false) // 不显示 loading
    }, intervalMs)
  }

  const stopPolling = () => {
    if (pollingIntervalRef.current) {
      clearInterval(pollingIntervalRef.current)
      pollingIntervalRef.current = null
    }
  }

  const fetchProjects = async (showLoading = true) => {
    if (showLoading) {
      setLoading(true)
    }
    try {
      const res = await api.get('/api/projects/')
      setProjects(res.data)
      // 检查是否有项目还在解析中，调整轮询频率
      const hasParsingProjects = res.data.some((p: Project) => p.status === 'pending' || p.status === 'parsing')
      if (hasParsingProjects) {
        // 如果有正在解析的项目，保持高频轮询（3秒）
        if (currentIntervalMs !== 3000) {
          startPolling(3000)
        }
      } else {
        // 如果没有正在解析的项目，降低轮询频率（10秒）
        if (currentIntervalMs !== 10000) {
          startPolling(10000)
        }
      }
    } catch (error) {
      if (showLoading) {
        message.error('获取项目列表失败')
      }
    } finally {
      if (showLoading) {
        setLoading(false)
      }
    }
  }

  const handleCreate = async (values: any) => {
    try {
      const res = await api.post('/api/projects/', values)
      const projectId = res.data.id
      message.success('项目创建成功，开始解析...')
      // 自动触发解析
      await api.post(`/api/projects/${projectId}/parser/start`, {})
      setModalVisible(false)
      form.resetFields()
      fetchProjects()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await api.delete(`/api/projects/${id}`)
      message.success('删除成功')
      fetchProjects()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleSync = async (id: string) => {
    try {
      await api.post(`/api/projects/${id}/sync`)
      message.success('同步成功，开始重新解析...')
      // 自动触发重新解析
      await api.post(`/api/projects/${id}/parser/start`, {})
      fetchProjects()
    } catch (error: any) {
      const detail = error?.response?.data?.detail || '同步失败'
      message.error(detail)
    }
  }

  const columns = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '来源',
      dataIndex: 'source_type',
      key: 'source_type',
      render: (type: string) => type === 'git' ? 'Git 仓库' : '本地目录',
    },
    {
      title: '地址',
      dataIndex: 'source_url',
      key: 'source_url',
      ellipsis: true,
    },
    {
      title: '分支',
      dataIndex: 'current_branch',
      key: 'current_branch',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          pending: { color: 'default', text: '待解析' },
          parsing: { color: 'processing', text: '解析中' },
          ready: { color: 'success', text: '就绪' },
          error: { color: 'error', text: '错误' },
        }
        const config = statusMap[status] || statusMap.pending
        return <Badge status={config.color as any} text={config.text} />
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: any, record: Project) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => window.location.href = `/projects/${record.id}/architecture`}
          >
            查看
          </Button>
          <Button
            type="link"
            icon={<SyncOutlined />}
            onClick={() => handleSync(record.id)}
            disabled={record.source_type !== 'git'}
            title={record.source_type !== 'git' ? '仅 Git 仓库支持同步' : ''}
          >
            同步
          </Button>
          <Popconfirm
            title="确定删除此项目？"
            onConfirm={() => handleDelete(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>项目列表</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
          新建项目
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={projects}
        rowKey="id"
        loading={loading}
      />

      <Modal
        title="新建项目"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleCreate} layout="vertical" initialValues={{ branch: "main" }}>
          <Form.Item name="name" label="项目名称" rules={[{ required: true }]}>
            <Input placeholder="请输入项目名称" />
          </Form.Item>
          <Form.Item name="source_type" label="来源类型" rules={[{ required: true }]}>
            <Select>
              <Select.Option value="git">Git 仓库</Select.Option>
              <Select.Option value="local">本地目录</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item name="source_url" label="仓库地址/目录路径" rules={[{ required: true }]}>
            <Input placeholder="https://github.com/user/repo.git 或 /path/to/project" />
          </Form.Item>
          <Form.Item name="branch" label="分支">
            <Input placeholder="main" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
