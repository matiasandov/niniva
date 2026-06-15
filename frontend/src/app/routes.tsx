import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Dashboard } from "./pages/Dashboard";
import { LiveSession } from "./pages/LiveSession";
import { MotorTests } from "./pages/MotorTests";
import { PatientProfile } from "./pages/PatientProfile";
import { PatientList } from "./pages/PatientList";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Dashboard },
      { path: "live", Component: LiveSession },
      { path: "tests", Component: MotorTests },
      { path: "patients", Component: PatientList },
      { path: "patients/:id", Component: PatientProfile },
    ],
  },
]);
