export async function api(path: string, method='GET', data?: unknown) {
  const res = await fetch('/api/v1/' + path, {
    method, headers: {'Content-Type':'application/json','X-Vertetify':'workspace'},
    body: data === undefined ? undefined : JSON.stringify(data)
  })
  if (!res.ok) throw new Error(res.status === 401 ? 'Sign-in required.' : 'Request failed. Check your input and try again.')
  return res.json()
}
