import api from './index'

export function uploadTextbook(file, name, version) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  if (version) formData.append('version', version)
  
  return api.post('/textbooks/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function parseTextbook(textbookId, unitNumbers = null) {
  return api.post(`/textbooks/${textbookId}/parse`, {
    unit_numbers: unitNumbers
  })
}

export function getTextbooks() {
  return api.get('/textbooks')
}

export function getTextbook(textbookId) {
  return api.get(`/textbooks/${textbookId}`)
}

export function deleteTextbook(textbookId) {
  return api.delete(`/textbooks/${textbookId}`)
}

export function getKnowledgePoints(textbookId, params = {}) {
  return api.get(`/textbooks/${textbookId}/knowledge`, { params })
}
