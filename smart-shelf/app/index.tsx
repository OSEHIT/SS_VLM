import { router, useFocusEffect } from "expo-router";
import { useCallback, useState } from "react";
import {
  ActivityIndicator,
  Image,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { fetchProducts, friendlyError, type Product } from "../services/api";

export default function Index() {
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      loadProducts();
    }, [])
  );

  const loadProducts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await fetchProducts();
      setProducts(result);
    } catch (err: any) {
      setError(friendlyError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getImageSource = (product: Product) => {
    if (product.display_image) {
      return { uri: product.display_image };
    }
    if (product.image_base64) {
      return { uri: `data:image/png;base64,${product.image_base64}` };
    }
    if (product.image_url) {
      return { uri: product.image_url };
    }
    return undefined;
  };

  return (
    <View style={{ flex: 1 }}>
      <ScrollView contentContainerStyle={styles.container}>
        {isLoading ? (
          <ActivityIndicator
            size="large"
            color="#4CAF50"
            style={{ marginTop: 20 }}
          />
        ) : error ? (
          <Text style={[styles.message, { color: "red" }]}>Error: {error}</Text>
        ) : products.length > 0 ? (
          products.map((product) => {
            const imageSource = getImageSource(product);

            return (
              <TouchableOpacity
                key={product.id}
                onPress={() =>
                  router.push({
                    pathname: "/ProductDetail",
                    params: { id: product.id },
                  })
                }
                style={styles.card}
              >
                {imageSource && (
                  <Image source={imageSource} style={styles.image} />
                )}
                <View style={styles.info}>
                  <Text style={styles.name}>
                    {product.product_name || "Unknown"}
                  </Text>
                  {product.brand && (
                    <Text style={styles.detailText}>
                      Brand: {product.brand}
                    </Text>
                  )}
                  <Text style={styles.type}>{product.product_type}</Text>
                  {product.quantity != null && (
                    <Text style={styles.count}>
                      Quantity: {product.quantity}
                    </Text>
                  )}
                  {product.expiry_date && (
                    <Text style={styles.detailText}>
                      Expires: {product.expiry_date}
                    </Text>
                  )}
                </View>
              </TouchableOpacity>
            );
          })
        ) : (
          <Text style={styles.message}>No products found.</Text>
        )}
      </ScrollView>

      <TouchableOpacity
        style={styles.button}
        onPress={() => router.push("/scan")}
      >
        <Text style={styles.buttonText}>Scan a product</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  card: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    alignItems: "center",
    elevation: 3,
    shadowColor: "#000",
    shadowOpacity: 0.1,
    shadowRadius: 6,
  },
  image: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  info: {
    marginLeft: 12,
    flex: 1,
  },
  name: {
    fontSize: 18,
    fontWeight: "600",
  },
  type: {
    fontSize: 14,
    color: "#888",
    marginVertical: 4,
  },
  count: {
    fontSize: 14,
    color: "#444",
  },
  detailText: {
    fontSize: 14,
    color: "#666",
    marginVertical: 2,
  },
  button: {
    backgroundColor: "#4CAF50",
    padding: 16,
    margin: 16,
    borderRadius: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  message: {
    textAlign: "center",
    marginTop: 20,
    fontSize: 16,
    color: "#555",
  },
});
