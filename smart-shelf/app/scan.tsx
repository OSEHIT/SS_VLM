import { CameraView, useCameraPermissions } from "expo-camera";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";
import { useRef, useState } from "react";
import {
  Image,
  ScrollView,
  StyleSheet,
  Switch,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { scanProduct, createProduct, friendlyError, type ScanResult } from "../services/api";
import { scheduleExpiryNotifications } from "../services/notifications";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface CapturedImage {
  uri: string;
}

// ===========================================================================
// Scan Screen
// ===========================================================================
export default function ScanScreen() {
  const router = useRouter();
  const [permission, requestPermission] = useCameraPermissions();
  const cameraRef = useRef<CameraView>(null);

  // Multi-image state
  const [images, setImages] = useState<CapturedImage[]>([]);
  const [reviewMode, setReviewMode] = useState(false);

  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [scanned, setScanned] = useState(false);
  const [barcodeData, setBarcodeData] = useState<string | null>(null);
  const [isBulk, setIsBulk] = useState(false);

  // -------------------------------------------------------------------------
  // Permission gates
  // -------------------------------------------------------------------------
  if (!permission) return <View />;

  if (!permission.granted) {
    return (
      <View style={styles.center}>
        <Text>Camera permission is required</Text>
        <TouchableOpacity onPress={requestPermission} style={styles.button}>
          <Text style={styles.buttonText}>Allow camera</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // -------------------------------------------------------------------------
  // Helpers
  // -------------------------------------------------------------------------
  const resetAll = () => {
    setImages([]);
    setReviewMode(false);
    setScanned(false);
    setBarcodeData(null);
    setSuccessMessage(null);
  };

  const removeImage = (index: number) => {
    setImages((prev) => prev.filter((_, i) => i !== index));
  };

  // -------------------------------------------------------------------------
  // Barcode
  // -------------------------------------------------------------------------
  const handleBarCodeScanned = ({
    type,
    data,
  }: {
    type: string;
    data: string;
  }) => {
    if (scanned || isBulk) return;
    setScanned(true);
    setBarcodeData(data);
    setSuccessMessage(`Barcode scanned: ${data} (Type: ${type})`);
  };

  // -------------------------------------------------------------------------
  // Capture & gallery
  // -------------------------------------------------------------------------
  const takePhoto = async () => {
    if (!cameraRef.current) return;
    try {
      const photo = await cameraRef.current.takePictureAsync({
        quality: 0.7,
        base64: false,
      });
      if (photo?.uri) {
        setImages((prev) => [...prev, { uri: photo.uri }]);
      }
    } catch (err) {
      console.error("Error taking photo:", err);
    }
  };

  const pickFromGallery = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsMultipleSelection: true,
      quality: 0.7,
    });

    if (!result.canceled && result.assets) {
      const newImages = result.assets.map((a) => ({ uri: a.uri }));
      setImages((prev) => [...prev, ...newImages]);
    }
  };

  // -------------------------------------------------------------------------
  // Analyse & submit
  // -------------------------------------------------------------------------
  const analyzePhotos = async () => {
    if (images.length === 0) return;
    setLoading(true);
    setSuccessMessage(null);
    try {
      const uris = images.map((img) => img.uri);
      const result: ScanResult = await scanProduct(uris, isBulk);

      // --- Programmer les notifications de péremption ---
      let notificationIds: string[] | null = null;
      if (result.expiry_date) {
        try {
          notificationIds = await scheduleExpiryNotifications(
            result.product_name || "Produit",
            result.expiry_date
          );
        } catch (notifErr) {
          console.warn("Failed to schedule notifications:", notifErr);
        }
      }

      await createProduct({
        product_name: result.product_name,
        brand: result.brand,
        expiry_date: result.expiry_date,
        ean: result.ean,
        product_type: result.product_type,
        quantity: result.quantity,
        source: result.source,
        confidence: result.confidence,
        image_url: result.image_url,
        image_base64: null,
        display_image: result.display_image,
        scan_id: result.scan_id,
        notification_ids: notificationIds,
      });

      const name = result.product_name || "Unknown product";
      const qty = result.quantity ? ` x${result.quantity}` : "";
      setSuccessMessage(`✅ ${name}${qty} added successfully!`);

      setTimeout(() => {
        setSuccessMessage(null);
        router.replace("/");
      }, 2000);
    } catch (err: any) {
      console.error("Error analyzing photos:", err.message);
      setSuccessMessage(`❌ ${friendlyError(err)}`);
    } finally {
      setLoading(false);
    }
  };

  // -------------------------------------------------------------------------
  // Thumbnail strip (shared between camera & review mode)
  // -------------------------------------------------------------------------
  const renderThumbnails = () => {
    if (images.length === 0) return null;
    return (
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.thumbnailStrip}
        contentContainerStyle={styles.thumbnailContent}
      >
        {images.map((img, index) => (
          <View key={`${img.uri}-${index}`} style={styles.thumbnailWrapper}>
            <Image source={{ uri: img.uri }} style={styles.thumbnail} />
            <TouchableOpacity
              style={styles.deleteButton}
              onPress={() => removeImage(index)}
            >
              <Text style={styles.deleteButtonText}>✕</Text>
            </TouchableOpacity>
          </View>
        ))}
      </ScrollView>
    );
  };

  // =========================================================================
  // RENDER
  // =========================================================================
  return (
    <View style={{ flex: 1 }}>
      {/* Bulk toggle */}
      <View style={styles.toggleContainer}>
        <Text style={styles.toggleLabel}>Produit en Vrac</Text>
        <Switch
          value={isBulk}
          onValueChange={setIsBulk}
          trackColor={{ false: "#ddd", true: "#81C784" }}
          thumbColor={isBulk ? "#4CAF50" : "#f4f3f4"}
        />
      </View>

      {/* Success / error toast */}
      {successMessage && (
        <View style={styles.toast}>
          <Text style={{ color: "white", textAlign: "center" }}>
            {successMessage}
          </Text>
        </View>
      )}

      {/* ---- REVIEW MODE ---- */}
      {reviewMode ? (
        <View style={styles.reviewContainer}>
          <Text style={styles.reviewTitle}>
            {images.length} photo{images.length > 1 ? "s" : ""} captured
          </Text>
          {isBulk && (
            <Text style={styles.bulkBadge}>🥕 Mode Vrac activé</Text>
          )}

          {/* Large preview scroll */}
          <ScrollView
            horizontal
            pagingEnabled
            showsHorizontalScrollIndicator={false}
            style={styles.previewScroll}
            contentContainerStyle={styles.previewContent}
          >
            {images.map((img, index) => (
              <Image
                key={`preview-${index}`}
                source={{ uri: img.uri }}
                style={styles.previewImage}
              />
            ))}
          </ScrollView>

          {/* Thumbnails */}
          {renderThumbnails()}

          {/* Actions */}
          <TouchableOpacity
            style={styles.button}
            onPress={analyzePhotos}
            disabled={loading || images.length === 0}
          >
            <Text style={styles.buttonText}>
              {loading ? "Adding product..." : "Add Product"}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.retakeButton]}
            onPress={resetAll}
          >
            <Text style={styles.buttonText}>Retake</Text>
          </TouchableOpacity>
        </View>
      ) : (
        /* ---- CAMERA MODE ---- */
        <>
          {barcodeData ? (
            <View style={styles.center}>
              <Text style={{ fontSize: 20, marginBottom: 20 }}>
                Scanned Barcode: {barcodeData}
              </Text>
              <TouchableOpacity style={styles.button} onPress={resetAll}>
                <Text style={styles.buttonText}>Scan Again</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <View style={{ flex: 1 }}>
              {/* Camera */}
              <CameraView
                ref={cameraRef}
                style={{ flex: 1 }}
                onBarcodeScanned={
                  scanned || isBulk ? undefined : handleBarCodeScanned
                }
              />

              {/* Thumbnail strip (above controls) */}
              {renderThumbnails()}

              {/* Bottom control bar: Gallery | Shutter | Validate */}
              <View style={styles.controlBar}>
                {/* Gallery */}
                <TouchableOpacity
                  style={styles.controlButton}
                  onPress={pickFromGallery}
                >
                  <Text style={styles.controlIcon}>🖼</Text>
                  <Text style={styles.controlLabel}>Gallery</Text>
                </TouchableOpacity>

                {/* Shutter */}
                <TouchableOpacity
                  style={styles.shutterButton}
                  onPress={takePhoto}
                >
                  <View style={styles.shutterInner} />
                </TouchableOpacity>

                {/* Validate */}
                {images.length > 0 ? (
                  <TouchableOpacity
                    style={[styles.controlButton, styles.validateButton]}
                    onPress={() => setReviewMode(true)}
                  >
                    <Text style={styles.validateIcon}>✓</Text>
                    <Text style={styles.validateLabel}>
                      Validate ({images.length})
                    </Text>
                  </TouchableOpacity>
                ) : (
                  <View style={styles.controlButton} />
                )}
              </View>
            </View>
          )}
        </>
      )}
    </View>
  );
}

// ===========================================================================
// Styles
// ===========================================================================
const styles = StyleSheet.create({
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  button: {
    marginTop: 16,
    paddingVertical: 14,
    paddingHorizontal: 32,
    backgroundColor: "#4CAF50",
    borderRadius: 8,
    alignItems: "center",
  },
  retakeButton: {
    backgroundColor: "#f44336",
    marginTop: 10,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },

  // Toggle ------------------------------------------------------------------
  toggleContainer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#f5f5f5",
    borderBottomWidth: 1,
    borderBottomColor: "#e0e0e0",
  },
  toggleLabel: {
    fontSize: 16,
    fontWeight: "600",
    color: "#333",
  },

  // Toast -------------------------------------------------------------------
  toast: {
    position: "absolute",
    top: 60,
    left: 0,
    right: 0,
    zIndex: 10,
    backgroundColor: "rgba(0,0,0,0.7)",
    padding: 10,
    borderRadius: 5,
    marginHorizontal: 16,
  },
  bulkBadge: {
    marginTop: 8,
    fontSize: 14,
    color: "#4CAF50",
    fontWeight: "600",
  },

  // Control bar -------------------------------------------------------------
  controlBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-around",
    paddingVertical: 16,
    paddingHorizontal: 12,
    backgroundColor: "#111",
  },
  controlButton: {
    width: 70,
    alignItems: "center",
    justifyContent: "center",
  },
  controlIcon: {
    fontSize: 24,
  },
  controlLabel: {
    color: "#ccc",
    fontSize: 11,
    marginTop: 4,
  },

  // Shutter -----------------------------------------------------------------
  shutterButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    borderWidth: 4,
    borderColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
  shutterInner: {
    width: 58,
    height: 58,
    borderRadius: 29,
    backgroundColor: "#fff",
  },

  // Validate ----------------------------------------------------------------
  validateButton: {
    backgroundColor: "#4CAF50",
    borderRadius: 20,
    paddingVertical: 8,
    paddingHorizontal: 10,
    width: "auto",
  },
  validateIcon: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "700",
  },
  validateLabel: {
    color: "#fff",
    fontSize: 10,
    marginTop: 2,
    fontWeight: "600",
  },

  // Thumbnails --------------------------------------------------------------
  thumbnailStrip: {
    maxHeight: 80,
    backgroundColor: "rgba(0,0,0,0.6)",
    paddingVertical: 8,
  },
  thumbnailContent: {
    paddingHorizontal: 8,
    alignItems: "center",
  },
  thumbnailWrapper: {
    marginHorizontal: 4,
    position: "relative",
  },
  thumbnail: {
    width: 60,
    height: 60,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: "#fff",
  },
  deleteButton: {
    position: "absolute",
    top: -6,
    right: -6,
    backgroundColor: "#f44336",
    width: 20,
    height: 20,
    borderRadius: 10,
    alignItems: "center",
    justifyContent: "center",
  },
  deleteButtonText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "700",
    lineHeight: 14,
  },

  // Review mode -------------------------------------------------------------
  reviewContainer: {
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 16,
    backgroundColor: "#fafafa",
  },
  reviewTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#333",
    marginBottom: 4,
  },
  previewScroll: {
    maxHeight: 220,
    marginTop: 12,
  },
  previewContent: {
    alignItems: "center",
    gap: 12,
    paddingHorizontal: 8,
  },
  previewImage: {
    width: 200,
    height: 200,
    borderRadius: 12,
    marginHorizontal: 6,
  },
});
