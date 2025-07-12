import { Link } from 'react-router-dom'
import './NavBar.css'

function NavBar() {
  return (
    <nav className="navbar">
      <Link to="/">Главная</Link>
      <Link to="/book/1">Книга 1</Link>
      <Link to="/book/2">Книга 2</Link>
      <Link to="/book/3">Книга 3</Link>
    </nav>
  )
}

export default NavBar
