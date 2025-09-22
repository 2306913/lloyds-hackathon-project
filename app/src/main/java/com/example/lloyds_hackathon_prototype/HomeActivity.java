package com.example.lloyds_hackathon_prototype;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.firestore.FirebaseFirestore;
import com.google.firebase.firestore.QueryDocumentSnapshot;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class HomeActivity extends AppCompatActivity {

    // Firebase
    private FirebaseFirestore db;
    private FirebaseAuth mAuth;

    // UI Elements
    private EditText searchInput;
    private ListView productListView;
    private Button addProductButton;

    // Data
    private List<Product> allProducts;
    private List<String> displayProducts;
    private ArrayAdapter<String> adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);

        // Initialize Firebase
        db = FirebaseFirestore.getInstance();
        mAuth = FirebaseAuth.getInstance();

        // Initialize UI elements
        searchInput = findViewById(R.id.searchInput);
        productListView = findViewById(R.id.productListView);
        addProductButton = findViewById(R.id.addProductButton);

        // Initialize data lists
        allProducts = new ArrayList<>();
        displayProducts = new ArrayList<>();

        // Set up adapter for ListView
        adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_2, android.R.id.text1, displayProducts);
        productListView.setAdapter(adapter);

        // Set up search functionality
        setupSearch();

        // Set up button listeners
        setupButtons();

        // Load products from Firebase
        loadProducts();

        // UNCOMMENT THE LINE BELOW TO ADD SAMPLE DATA (RUN ONCE, THEN COMMENT OUT)
        // addSampleProducts();
    }

    private void setupSearch() {
        searchInput.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                filterProducts(s.toString());
            }

            @Override
            public void afterTextChanged(Editable s) {}
        });
    }

    private void setupButtons() {
        addProductButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Navigate to Add Product page
                Intent intent = new Intent(HomeActivity.this, AddProductActivity.class);
                startActivity(intent);
            }
        });
    }

    private void filterProducts(String searchText) {
        displayProducts.clear();

        if (searchText.isEmpty()) {
            // Show all products
            for (Product product : allProducts) {
                displayProducts.add(formatProductForDisplay(product));
            }
        } else {
            // Filter products based on search text
            String searchLower = searchText.toLowerCase();
            for (Product product : allProducts) {
                if (productMatchesSearch(product, searchLower)) {
                    displayProducts.add(formatProductForDisplay(product));
                }
            }
        }

        adapter.notifyDataSetChanged();
    }

    private boolean productMatchesSearch(Product product, String searchLower) {
        // Search through multiple fields
        return (product.name != null && product.name.toLowerCase().contains(searchLower)) ||
                (product.description != null && product.description.toLowerCase().contains(searchLower)) ||
                (product.category != null && product.category.toLowerCase().contains(searchLower)) ||
                (product.storeName != null && product.storeName.toLowerCase().contains(searchLower)) ||
                (product.storeAddress != null && product.storeAddress.toLowerCase().contains(searchLower)) ||
                (product.tags != null && product.tags.toLowerCase().contains(searchLower));
    }

    private String formatProductForDisplay(Product product) {
        StringBuilder display = new StringBuilder();
        display.append(product.name);
        display.append(" - £").append(String.format("%.2f", product.price));

        if (product.storeName != null && !product.storeName.isEmpty()) {
            display.append("\nStore: ").append(product.storeName);
        }

        if (product.quantity > 0) {
            display.append(" | Qty: ").append(product.quantity);
        }

        if (product.description != null && !product.description.isEmpty()) {
            display.append("\n").append(product.description);
        }

        return display.toString();
    }

    private void loadProducts() {
        db.collection("products")
                .get()
                .addOnCompleteListener(task -> {
                    if (task.isSuccessful()) {
                        allProducts.clear();

                        for (QueryDocumentSnapshot document : task.getResult()) {
                            try {
                                Product product = new Product();
                                product.id = document.getId();
                                product.name = document.getString("name");
                                product.description = document.getString("description");
                                product.category = document.getString("category");
                                product.storeName = document.getString("storeName");
                                product.storeAddress = document.getString("storeAddress");
                                product.tags = document.getString("tags");

                                // Handle price - could be stored as String or Number
                                Object priceObj = document.get("price");
                                if (priceObj instanceof Number) {
                                    product.price = ((Number) priceObj).doubleValue();
                                } else if (priceObj instanceof String) {
                                    try {
                                        product.price = Double.parseDouble((String) priceObj);
                                    } catch (NumberFormatException e) {
                                        product.price = 0.0;
                                    }
                                }

                                // Handle quantity
                                Object quantityObj = document.get("quantity");
                                if (quantityObj instanceof Number) {
                                    product.quantity = ((Number) quantityObj).intValue();
                                } else if (quantityObj instanceof String) {
                                    try {
                                        product.quantity = Integer.parseInt((String) quantityObj);
                                    } catch (NumberFormatException e) {
                                        product.quantity = 0;
                                    }
                                }

                                // Validate product has required fields
                                if (product.name != null && product.description != null) {
                                    allProducts.add(product);
                                }

                            } catch (Exception e) {
                                Log.w("HomeActivity", "Error parsing product: " + document.getId(), e);
                            }
                        }

                        // Update display
                        filterProducts(searchInput.getText().toString());

                        Toast.makeText(HomeActivity.this,
                                "Loaded " + allProducts.size() + " products",
                                Toast.LENGTH_SHORT).show();

                        Log.d("HomeActivity", "Successfully loaded " + allProducts.size() + " products");

                    } else {
                        Log.w("HomeActivity", "Error getting products.", task.getException());
                        Toast.makeText(HomeActivity.this,
                                "Failed to load products: " + task.getException().getMessage(),
                                Toast.LENGTH_LONG).show();
                    }
                });
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Reload products when returning from Add Product page
        loadProducts();
    }

    /**
     * TESTING METHOD - Add sample products to Firestore
     * Call this method once to populate your database with test data
     * You can call this from onCreate() initially, then remove it
     */
    private void addSampleProducts() {
        // Create sample products with new structure
        Object[][] sampleData = {
                {"Gaming Laptop", "TechStore Plus", "123 High Street, London", "High-performance gaming laptop with RTX graphics", 5, 999.99, "electronics, gaming, laptop, computer"},
                {"Organic Coffee", "Bean There Cafe", "456 Coffee Lane, Manchester", "Fresh roasted organic coffee beans", 20, 12.99, "food, coffee, organic, beans"},
                {"Programming Book", "BookWorld", "789 Knowledge Ave, Birmingham", "Complete guide to Java programming", 15, 29.99, "books, education, programming, java"},
                {"Wireless Headphones", "Sound Solutions", "321 Music Street, Liverpool", "Noise-cancelling wireless headphones", 8, 199.99, "electronics, audio, headphones, wireless"},
                {"Indoor Plant", "Green Thumb Garden", "654 Garden Road, Edinburgh", "Beautiful indoor plant perfect for offices", 12, 24.99, "plants, home, decor, indoor"},
                {"Smartphone", "Mobile Mania", "987 Phone Plaza, Cardiff", "Latest model with advanced camera features", 3, 799.99, "electronics, mobile, smartphone, camera"},
                {"Office Chair", "Furniture First", "147 Comfort Close, Bristol", "Ergonomic office chair for all-day comfort", 6, 149.99, "furniture, office, chair, ergonomic"},
                {"Water Bottle", "Fitness Gear", "258 Health Highway, Leeds", "Stainless steel insulated water bottle", 25, 19.99, "sports, fitness, water, bottle"}
        };

        for (Object[] productData : sampleData) {
            Map<String, Object> product = new HashMap<>();
            product.put("name", productData[0]);
            product.put("storeName", productData[1]);
            product.put("storeAddress", productData[2]);
            product.put("description", productData[3]);
            product.put("quantity", productData[4]);
            product.put("price", productData[5]);
            product.put("tags", productData[6]);
            product.put("businessUserId", "sample");
            product.put("dateAdded", System.currentTimeMillis());

            // Add legacy category field
            String tags = (String) productData[6];
            if (tags.contains("electronics")) {
                product.put("category", "Electronics");
            } else if (tags.contains("food")) {
                product.put("category", "Food & Drink");
            } else if (tags.contains("books")) {
                product.put("category", "Education");
            } else {
                product.put("category", "General");
            }

            db.collection("products")
                    .add(product)
                    .addOnSuccessListener(documentReference ->
                            Log.d("HomeActivity", "Sample product added: " + productData[0]))
                    .addOnFailureListener(e ->
                            Log.w("HomeActivity", "Error adding sample product", e));
        }

        Toast.makeText(this, "Adding sample products to database...", Toast.LENGTH_SHORT).show();
    }

    // Updated Product class to hold new product data
    public static class Product {
        public String id;
        public String name;
        public String description;
        public String category;
        public String storeName;
        public String storeAddress;
        public String tags;
        public double price;
        public int quantity;

        public Product() {
            // Default constructor required for Firestore
            this.name = "";
            this.description = "";
            this.category = "";
            this.storeName = "";
            this.storeAddress = "";
            this.tags = "";
            this.price = 0.0;
            this.quantity = 0;
        }
    }
}