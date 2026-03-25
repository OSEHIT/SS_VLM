import { router, useFocusEffect, useLocalSearchParams } from "expo-router";
import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { fetchProduct, deleteProduct, type Product } from "../services/api";
import { cancelNotifications } from "../services/notifications";

export default function ProductDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      const load = async () => {
        if (!id) return;

        setIsLoading(true);
        setError(null);
        try {
          const result = await fetchProduct(id);
          setProduct(result);
        } catch (err: any) {
          setError(err.message);
        } finally {
          setIsLoading(false);
        }
      };

      load();
    }, [id])
  );

  const handleEdit = () => {
    router.push({ pathname: "/ProductEdit", params: { id } });
  };

  const handleDelete = () => {
    Alert.alert("Delete Product", "Are you sure you want to delete this product?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            // Annuler less notifications programmées
            if (product?.notification_ids && product.notification_ids.length > 0) {
              await cancelNotifications(product.notification_ids);
            }
            await deleteProduct(id!);
            Alert.alert("Success", "Product deleted successfully!");
            router.back();
          } catch (err: any) {
            Alert.alert("Error", `Failed to delete product: ${err.message}`);
          }
        },
        style: "destructive",
      },
    ]);
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text>Loading product details...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>Error: {error}</Text>
      </View>
    );
  }

  if (!product) {
    return (
      <View style={styles.container}>
        <Text>No product found for ID: {id}</Text>
      </View>
    );
  }

  const imageSource = product.display_image
    ? { uri: product.display_image }
    : product.image_base64
      ? { uri: `data:image/png;base64,${product.image_base64}` }
      : product.image_url
        ? { uri: product.image_url }
        : undefined;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Product Details</Text>
      {imageSource && (
        <Image source={imageSource} style={styles.productImage} />
      )}
      <Text style={styles.detailText}>
        Name: {product.product_name || "Unknown"}
      </Text>
      {product.brand && (
        <Text style={styles.detailText}>Brand: {product.brand}</Text>
      )}
      <Text style={styles.detailText}>Type: {product.product_type}</Text>
      {product.quantity != null && (
        <Text style={styles.detailText}>Quantity: {product.quantity}</Text>
      )}
      {product.expiry_date && (
        <Text style={styles.detailText}>Expires: {product.expiry_date}</Text>
      )}
      {product.ean && (
        <Text style={styles.detailText}>EAN: {product.ean}</Text>
      )}
      {product.source && (
        <Text style={styles.detailText}>Source: {product.source}</Text>
      )}

      <View style={styles.buttonContainer}>
        <TouchableOpacity style={styles.editButton} onPress={handleEdit}>
          <Text style={styles.buttonText}>Edit</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.deleteButton} onPress={handleDelete}>
          <Text style={styles.buttonText}>Delete</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    alignItems: "center",
    justifyContent: "flex-start",
    backgroundColor: "#f5f5f5",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    marginBottom: 20,
    color: "#333",
  },
  productImage: {
    width: 200,
    height: 200,
    borderRadius: 10,
    marginBottom: 20,
    resizeMode: "contain",
    backgroundColor: "#e0e0e0",
  },
  detailText: {
    fontSize: 18,
    marginBottom: 10,
    color: "#555",
  },
  errorText: {
    fontSize: 18,
    color: "red",
    textAlign: "center",
  },
  buttonContainer: {
    flexDirection: "row",
    marginTop: 30,
    width: "80%",
    justifyContent: "space-around",
  },
  editButton: {
    backgroundColor: "#2196F3",
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
  },
  deleteButton: {
    backgroundColor: "#F44336",
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "600",
  },
});
