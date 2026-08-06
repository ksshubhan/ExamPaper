import { Outlet } from 'react-router-dom'
import Header from './components/Header'

export default function App() {
  return (
    <div className="min-h-svh bg-[var(--bg)] text-[var(--text)]">
      <Header />
      <main>
        <Outlet />
      </main>
    </div>
  )
}
