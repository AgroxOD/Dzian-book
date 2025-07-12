import { Link } from 'react-router-dom'

function Home() {
  return (
    <div>
      <h1>Dzian Wiki</h1>
      <p>Добро пожаловать в веб-интерфейс проекта. Выберите анализ книги:</p>
      <ul>
        <li><Link to="/book/1">Книга 1</Link></li>
        <li><Link to="/book/2">Книга 2</Link></li>
        <li><Link to="/book/3">Книга 3</Link></li>
      </ul>
    </div>
  )
}

export default Home
