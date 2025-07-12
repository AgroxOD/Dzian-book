import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Home from './Home'
import Book from './Book'
import NavBar from './NavBar'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/book/:id" element={<Book />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
