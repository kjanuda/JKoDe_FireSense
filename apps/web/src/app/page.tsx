import ApiConnectionStatus from "@/components/dashboard/ApiConnectionStatus";
import FireSenseDashboard from "@/components/dashboard/FireSenseDashboard";


export default function Home() {
  return (
    <>
      <ApiConnectionStatus />

      <FireSenseDashboard />
    </>
  );
}
