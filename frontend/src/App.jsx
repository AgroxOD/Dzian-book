import { HashRouter, Routes, Route } from 'react-router-dom'
import Home from './Home'
import Book from './Book'
import NavBar from './NavBar'
import './App.css'

function App() {
  return (
    <HashRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/book/:id" element={<Book />} />
      </Routes>
    </HashRouter>
  )
}

export default App
