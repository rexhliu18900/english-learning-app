import api from './index'

export function generateTest(data) {
  return api.post('/tests/generate', data)
}

export function getTest(testId) {
  return api.get(`/tests/${testId}`)
}

export function submitTest(testId, answers) {
  return api.post(`/tests/${testId}/submit`, { answers })
}

export function getTestRecords(page = 1, pageSize = 10) {
  return api.get('/tests/records', { params: { page, page_size: pageSize } })
}

export function getStatistics() {
  return api.get('/tests/statistics')
}

export function generateReviewTest(wrongTestId) {
  return api.post(`/tests/review/${wrongTestId}`)
}

export function generateWrongTest(data) {
  return api.post('/tests/wrong-test', data)
}
