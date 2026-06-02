import { Button, Space, Dropdown, message } from 'antd'
import { DownloadOutlined, FileImageOutlined, FileTextOutlined } from '@ant-design/icons'
import { exportToPNG, exportToSVG, exportToJSON, exportToPDF } from '../../utils/exportUtils'

interface ExportToolbarProps {
  targetId: string
  filename?: string
  jsonData?: any
}

export default function ExportToolbar({ targetId, filename = 'codeviz-graph', jsonData }: ExportToolbarProps) {
  const handleExport = async (format: string) => {
    try {
      switch (format) {
        case 'png':
          await exportToPNG(targetId, `${filename}.png`)
          message.success('PNG 导出成功')
          break
        case 'svg':
          exportToSVG(targetId, `${filename}.svg`)
          message.success('SVG 导出成功')
          break
        case 'json':
          if (jsonData) {
            exportToJSON(jsonData, `${filename}.json`)
            message.success('JSON 导出成功')
          } else {
            message.warning('暂无数据可导出')
          }
          break
        case 'pdf':
          exportToPDF(targetId, `${filename}.pdf`)
          message.success('PDF 导出成功')
          break
      }
    } catch (error) {
      message.error(`导出失败: ${error}`)
    }
  }

  const items = [
    { key: 'png', label: 'PNG 图片', icon: <FileImageOutlined /> },
    { key: 'svg', label: 'SVG 矢量图', icon: <FileImageOutlined /> },
    { key: 'json', label: 'JSON 数据', icon: <FileTextOutlined /> },
    { key: 'pdf', label: 'PDF 文档', icon: <FileTextOutlined /> },
  ]

  return (
    <Dropdown
      menu={{
        items,
        onClick: ({ key }) => handleExport(key),
      }}
    >
      <Button icon={<DownloadOutlined />}>
        导出
      </Button>
    </Dropdown>
  )
}
