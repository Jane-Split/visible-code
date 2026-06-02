import { useState, useEffect, useRef } from 'react'
import Editor, { OnMount, OnChange } from '@monaco-editor/react'
import { Card, Select, Space, Button, message } from 'antd'
import { FileTextOutlined, ExpandOutlined } from '@ant-design/icons'
import api from '../../services/api'

interface CodePanelProps {
  projectId: string
  selectedEntityId?: string
  onEntitySelect?: (entityId: string) => void
}

interface Entity {
  id: string
  name: string
  qualified_name: string
  file_path: string
  start_line: number
  end_line: number
  type: string
}

export default function CodePanel({ projectId, selectedEntityId, onEntitySelect }: CodePanelProps) {
  const [code, setCode] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [entities, setEntities] = useState<Entity[]>([])
  const [currentFile, setCurrentFile] = useState<string>('')
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null)
  const editorRef = useRef<any>(null)

  useEffect(() => {
    if (projectId) {
      fetchEntities()
    }
  }, [projectId])

  useEffect(() => {
    if (selectedEntityId && entities.length > 0) {
      const entity = entities.find((e) => e.id === selectedEntityId)
      if (entity) {
        navigateToEntity(entity)
      }
    }
  }, [selectedEntityId, entities])

  const fetchEntities = async () => {
    try {
      const res = await api.get(`/api/projects/${projectId}/graphs/dependency`)
      const data = res.data
      
      // 提取文件列表
      const fileMap = new Map<string, Entity>()
      for (const node of data.nodes) {
        if (node.file_path && !fileMap.has(node.file_path)) {
          fileMap.set(node.file_path, {
            id: node.id,
            name: node.file_path.split('/').pop() || node.file_path,
            qualified_name: node.qualified_name,
            file_path: node.file_path,
            start_line: node.start_line,
            end_line: node.end_line,
            type: node.type,
          })
        }
      }
      
      setEntities(Array.from(fileMap.values()))
    } catch (error) {
      console.error('获取实体列表失败:', error)
    }
  }

  const loadFile = async (filePath: string) => {
    setLoading(true)
    try {
      // TODO: 实现文件内容获取 API
      // 暂时使用模拟数据
      setCode(getMockCode(filePath))
      setCurrentFile(filePath)
    } catch (error) {
      message.error('加载文件失败')
    } finally {
      setLoading(false)
    }
  }

  const navigateToEntity = (entity: Entity) => {
    setSelectedEntity(entity)
    if (entity.file_path !== currentFile) {
      loadFile(entity.file_path)
    }
    
    // 滚动到指定行
    setTimeout(() => {
      if (editorRef.current) {
        editorRef.current.revealLineInCenter(entity.start_line)
        editorRef.current.setSelection({
          startLineNumber: entity.start_line,
          startColumn: 1,
          endLineNumber: entity.end_line,
          endColumn: 1,
        })
      }
    }, 100)
  }

  const handleEditorMount: OnMount = (editor) => {
    editorRef.current = editor
  }

  const handleEditorChange: OnChange = (value) => {
    // 实时保存或其他处理
    console.log('Code changed:', value)
  }

  const getFileLanguage = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    const langMap: Record<string, string> = {
      java: 'java',
      ts: 'typescript',
      tsx: 'typescript',
      js: 'javascript',
      jsx: 'javascript',
      py: 'python',
      go: 'go',
    }
    return langMap[ext || ''] || 'plaintext'
  }

  // 模拟代码数据
  const getMockCode = (filePath: string): string => {
    const mockCodes: Record<string, string> = {
      'Main.java': `package com.example;

public class Main {
    private String name;
    
    public Main() {}
    
    public void sayHello() {
        System.out.println("Hello, " + name);
    }
    
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
}`,
      'UserService.java': `package com.example.service;

import com.example.Main;

public class UserService {
    private Main main;
    
    public void create() {
        main = new Main();
        main.setName("Test");
    }
    
    public void update() {
        if (main != null) {
            main.sayHello();
        }
    }
}`,
    }
    return mockCodes[filePath.split('/').pop() || ''] || '// 文件内容加载中...'
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Card size="small" style={{ marginBottom: 8 }}>
        <Space>
          <FileTextOutlined />
          <Select
            placeholder="选择文件"
            style={{ width: 300 }}
            value={currentFile || undefined}
            onChange={(value) => loadFile(value)}
            showSearch
            filterOption={(input, option) =>
              (option?.label as string)?.toLowerCase().includes(input.toLowerCase())
            }
            options={entities.map((e) => ({
              value: e.file_path,
              label: e.name,
            }))}
          />
          {selectedEntity && (
            <span style={{ fontSize: 12, color: '#666' }}>
              行 {selectedEntity.start_line} - {selectedEntity.end_line}
            </span>
          )}
        </Space>
      </Card>

      <div style={{ flex: 1, border: '1px solid #d9d9d9', borderRadius: 4, overflow: 'hidden' }}>
        <Editor
          height="100%"
          language={getFileLanguage(currentFile)}
          value={code}
          onChange={handleEditorChange}
          onMount={handleEditorMount}
          loading={<div>加载中...</div>}
          options={{
            readOnly: true,
            minimap: { enabled: true },
            fontSize: 13,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            folding: true,
            renderLineHighlight: 'all',
            selectOnLineNumbers: true,
          }}
          theme="vs"
        />
      </div>
    </div>
  )
}
