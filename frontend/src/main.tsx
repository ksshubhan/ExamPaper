import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import Home from './pages/Home.tsx'
import About from './pages/About.tsx'
import Pricing from './pages/Pricing.tsx'
import QualificationGrid from './pages/QualificationGrid.tsx'
import BoardGrid from './pages/BoardGrid.tsx'
import SubjectGrid from './pages/SubjectGrid.tsx'
import StudyView from './pages/StudyView.tsx'
import BuildPaper from './pages/BuildPaper.tsx'

const router = createBrowserRouter([
  {
    element: <App />,
    children: [
      { index: true, element: <Home /> },
      // Static routes out-rank the :feature param, so these never bounce.
      { path: 'about', element: <About /> },
      { path: 'pricing', element: <Pricing /> },
      // format -> qualification -> exam board -> subject -> study view
      { path: ':feature', element: <QualificationGrid /> },
      { path: ':feature/:qualification', element: <BoardGrid /> },
      { path: ':feature/:qualification/:board', element: <SubjectGrid /> },
      {
        path: ':feature/:qualification/:board/:subject',
        element: <StudyView />,
      },
      // Static 'build' segment out-ranks nothing here — it's a distinct depth.
      {
        path: ':feature/:qualification/:board/:subject/build',
        element: <BuildPaper />,
      },
    ],
  },
])

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>,
)
