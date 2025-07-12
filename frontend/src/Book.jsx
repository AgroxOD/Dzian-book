import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { marked } from 'marked'

function Book() {
  const { id } = useParams()
  const [content, setContent] = useState('')

  useEffect(() => {
    fetch(`analyses/book${id}.md`)
      .then((res) => res.text())
      .then((text) => setContent(marked.parse(text)))
  }, [id])

  return (
    <div>
      <h2>Анализ книги {id}</h2>
      <div dangerouslySetInnerHTML={{ __html: content }} />
    </div>
  )
}

export default Book
