import api from './index'

export function chat(message, textbookId = null) {
  return api.post('/chat/chat', {
    message,
    textbook_id: textbookId
  })
}

export function queryKnowledge(query, textbookId = null, params = {}) {
  return api.post('/chat/query', {
    query,
    textbook_id: textbookId
  }, { params })
}

export function explainKnowledge(knowledgePointId) {
  return api.post('/chat/explain', {
    knowledge_point_id: knowledgePointId
  })
}
