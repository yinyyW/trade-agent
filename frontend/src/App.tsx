import { Route, Routes } from "react-router-dom";
import LayoutContainer from "./components/common/LayoutContainer";
import HomePage from "./pages/home/HomePage";
import PlaceholderPage from "./pages/PlaceholderPage";
import StockPage from "./pages/stock/StockPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LayoutContainer />}>
        <Route index element={<HomePage />} />
        <Route path="/stock" element={<StockPage />} />
        <Route path="/qa" element={<PlaceholderPage title="AI问答" />} />
        <Route
          path="/watch-list"
          element={<PlaceholderPage title="自选股" />}
        />
        <Route
          path="*"
          element={
            <PlaceholderPage
              title="页面未找到"
              description="你访问的页面不存在"
            />
          }
        />
      </Route>
    </Routes>
  );
}

export default App;
