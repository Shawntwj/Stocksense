import logo from './logo.svg';
import './App.css';
import Dashboard from './dashboard/Dashboard';
import AppRoutes from './AppRoutes';
import { BrowserRouter } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <div className='container'>
          <AppRoutes />
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
