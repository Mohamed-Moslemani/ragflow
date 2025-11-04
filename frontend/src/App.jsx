import Navbar from "./components/Navbar";
import UploadForm from "./components/upload";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <UploadForm />
    </div>
  );
}
