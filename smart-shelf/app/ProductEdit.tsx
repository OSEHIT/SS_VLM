import { router, useLocalSearchParams } from "expo-router";
import { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from "react-native";
import {
  fetchProduct,
  updateProduct,
  submitRLFeedback,
  type Product,
} from "../services/api";

export default function ProductEdit() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [name, setName] = useState("");
  const [brand, setBrand] = useState("");
  const [quantity, setQuantity] = useState("");
  const [expiryDate, setExpiryDate] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      if (!id) {
        setError("Product ID not provided.");
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);
      try {
        const result = await fetchProduct(id);
        setProduct(result);
        setName(result.product_name || "");
        setBrand(result.brand || "");
        setQuantity(result.quantity != null ? String(result.quantity) : "");
        setExpiryDate(result.expiry_date || "");
      } catch (err: any) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    load();
  }, [id]);

  const handleSave = async () => {
    if (!product || !id) return;

    setIsLoading(true);
    setError(null);

    const updateData: Record<string, unknown> = {
      product_name: name || null,
      brand: brand || null,
      expiry_date: expiryDate || null,
    };

    // Only include quantity for bulk products
    if (product.product_type === "bulk" && quantity) {
      updateData.quantity = Number(quantity);
    }

    try {
      await updateProduct(id, updateData);

      // Submit RL feedback if scan_id exists
      if (product.scan_id) {
        await submitRLFeedback(product.scan_id, {
          product_name: name || null,
          brand: brand || null,
          expiry_date: expiryDate || null,
          quantity:
            product.product_type === "bulk" && quantity
              ? Number(quantity)
              : null,
        });
      }

      Alert.alert("Success", "Product updated successfully!");
      router.back();
    } catch (err: any) {
      setError(err.message);
      Alert.alert("Error", `Failed to update product: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text>Loading product for edit...</Text>
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

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Edit Product</Text>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Name:</Text>
        <TextInput style={styles.input} value={name} onChangeText={setName} />
      </View>

      <View style={styles.formGroup}>
        <Text style={styles.label}>Brand:</Text>
        <TextInput
          style={styles.input}
          value={brand}
          onChangeText={setBrand}
        />
      </View>

      {/* Only show quantity field for bulk products */}
      {product?.product_type === "bulk" && (
        <View style={styles.formGroup}>
          <Text style={styles.label}>Quantity (Vrac):</Text>
          <TextInput
            style={styles.input}
            value={quantity}
            onChangeText={setQuantity}
            keyboardType="numeric"
          />
        </View>
      )}

      <View style={styles.formGroup}>
        <Text style={styles.label}>Expiry Date (YYYY-MM-DD):</Text>
        <TextInput
          style={styles.input}
          value={expiryDate}
          onChangeText={setExpiryDate}
          placeholder="YYYY-MM-DD"
        />
      </View>

      <TouchableOpacity style={styles.saveButton} onPress={handleSave}>
        <Text style={styles.buttonText}>Save Changes</Text>
      </TouchableOpacity>

      {product?.scan_id && (
        <Text style={styles.rlNote}>
          ✅ Les corrections seront aussi envoyées pour l'entraînement RL
        </Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    alignItems: "center",
    backgroundColor: "#f5f5f5",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    marginBottom: 30,
    color: "#333",
  },
  formGroup: {
    width: "90%",
    marginBottom: 15,
  },
  label: {
    fontSize: 16,
    marginBottom: 5,
    color: "#555",
    fontWeight: "bold",
  },
  input: {
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
    color: "#333",
  },
  saveButton: {
    backgroundColor: "#4CAF50",
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginTop: 30,
    width: "90%",
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 18,
    fontWeight: "600",
  },
  errorText: {
    fontSize: 18,
    color: "red",
    textAlign: "center",
  },
  rlNote: {
    marginTop: 16,
    fontSize: 13,
    color: "#888",
    textAlign: "center",
  },
});
