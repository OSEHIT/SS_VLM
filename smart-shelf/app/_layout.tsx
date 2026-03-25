import { Stack } from "expo-router";
import { useEffect } from "react";
import { requestNotificationPermission } from "../services/notifications";

export default function RootLayout() {
  useEffect(() => {
    requestNotificationPermission();
  }, []);

  return (
    <Stack>
      <Stack.Screen name="index" options={{ title: "Home" }} />
    </Stack>
  );
}
