// =============================================================================
// Smart Shelf V2 — Local Notifications Service
// =============================================================================
// Gestion des notifications de péremption (J-3 et J-0).
// =============================================================================

import * as Notifications from "expo-notifications";

// ---------------------------------------------------------------------------
// Configuration du handler (affichage en foreground)
// ---------------------------------------------------------------------------
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldFlashScreen: false,
  }),
});

// ---------------------------------------------------------------------------
// Permission
// ---------------------------------------------------------------------------

/**
 * Demande la permission de notifications à l'utilisateur.
 * Retourne true si accordée.
 */
export async function requestNotificationPermission(): Promise<boolean> {
  const { status: existing } = await Notifications.getPermissionsAsync();
  if (existing === "granted") return true;

  const { status } = await Notifications.requestPermissionsAsync();
  return status === "granted";
}

// ---------------------------------------------------------------------------
// Scheduling
// ---------------------------------------------------------------------------

/**
 * Programme les notifications de péremption pour un produit :
 * - J-3 : "Attention, {name} expire dans 3 jours !"
 * - J-0 : "{name} expire aujourd'hui !"
 *
 * @returns Liste des notification IDs programmés (pour annulation future)
 */
export async function scheduleExpiryNotifications(
  productName: string,
  expiryDateStr: string
): Promise<string[]> {
  const ids: string[] = [];
  const expiry = new Date(expiryDateStr + "T09:00:00");
  const now = new Date();

  const name = productName || "Votre produit";

  // --- J-3 notification ---
  const j3 = new Date(expiry);
  j3.setDate(j3.getDate() - 3);

  if (j3 > now) {
    const secondsUntilJ3 = Math.floor((j3.getTime() - now.getTime()) / 1000);
    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: "⚠️ Péremption proche",
        body: `Attention, ${name} expire dans 3 jours !`,
        data: { type: "expiry_warning" },
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
        seconds: secondsUntilJ3,
        repeats: false,
      },
    });
    ids.push(id);
  }

  // --- J-0 notification ---
  if (expiry > now) {
    const secondsUntilJ0 = Math.floor(
      (expiry.getTime() - now.getTime()) / 1000
    );
    const id = await Notifications.scheduleNotificationAsync({
      content: {
        title: "🚨 Expiration aujourd'hui",
        body: `${name} expire aujourd'hui !`,
        data: { type: "expiry_today" },
      },
      trigger: {
        type: Notifications.SchedulableTriggerInputTypes.TIME_INTERVAL,
        seconds: secondsUntilJ0,
        repeats: false,
      },
    });
    ids.push(id);
  }

  return ids;
}

// ---------------------------------------------------------------------------
// Cancellation
// ---------------------------------------------------------------------------

/**
 * Annule les notifications programmées par leurs IDs.
 */
export async function cancelNotifications(ids: string[]): Promise<void> {
  for (const id of ids) {
    await Notifications.cancelScheduledNotificationAsync(id);
  }
}
