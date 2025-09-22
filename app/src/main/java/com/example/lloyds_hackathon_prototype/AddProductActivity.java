package com.example.lloyds_hackathon_prototype;

import android.content.Intent;
import android.os.Bundle;
import android.text.TextUtils;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;
import com.google.firebase.firestore.FirebaseFirestore;

import java.util.HashMap;
import java.util.Map;

public class AddProductActivity extends AppCompatActivity {

    // Firebase
    private FirebaseFirestore db;
    private FirebaseAuth mAuth;

    // UI Elements
    private EditText productNameInput;
    private EditText storeNameInput;
    private EditText storeAddressInput;
    private EditText productDescriptionInput;
    private EditText productQuantityInput;
    private EditText productTagsInput;
    private EditText productPriceInput;
    private Button addProductButton;
    private Button cancelButton;

    private String currentUserId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_product);

        // Initialize Firebase
        db = FirebaseFirestore.getInstance();
        mAuth = FirebaseAuth.getInstance();

        // Get current user
        FirebaseUser user = mAuth.getCurrentUser();
        if (user != null) {
            currentUserId = user.getUid();
        } else {
            // User not logged in, redirect to login
            Toast.makeText(this, "Please log in to add products", Toast.LENGTH_SHORT).show();
            startActivity(new Intent(this, LoginActivity.class));
            finish();
            return;
        }

        // Initialize UI elements
        initializeViews();

        // Set up button listeners
        setupButtonListeners();
    }

    private void initializeViews() {
        productNameInput = findViewById(R.id.productNameInput);
        storeNameInput = findViewById(R.id.storeNameInput);
        storeAddressInput = findViewById(R.id.storeAddressInput);
        productDescriptionInput = findViewById(R.id.productDescriptionInput);
        productQuantityInput = findViewById(R.id.productQuantityInput);
        productTagsInput = findViewById(R.id.productTagsInput);
        productPriceInput = findViewById(R.id.productPriceInput);
        addProductButton = findViewById(R.id.addProductButton);
        cancelButton = findViewById(R.id.cancelButton);
    }

    private void setupButtonListeners() {
        addProductButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                addProduct();
            }
        });

        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish(); // Go back to previous activity
            }
        });
    }

    private void addProduct() {
        // Get input values and trim whitespace
        String productName = productNameInput.getText().toString().trim();
        String storeName = storeNameInput.getText().toString().trim();
        String storeAddress = storeAddressInput.getText().toString().trim();
        String productDescription = productDescriptionInput.getText().toString().trim();
        String quantityStr = productQuantityInput.getText().toString().trim();
        String tags = productTagsInput.getText().toString().trim();
        String priceStr = productPriceInput.getText().toString().trim();

        // Validate required fields
        if (!validateInputs(productName, storeName, productDescription, quantityStr, priceStr)) {
            return;
        }

        // Parse numeric values
        int quantity;
        double price;
        try {
            quantity = Integer.parseInt(quantityStr);
            price = Double.parseDouble(priceStr);
        } catch (NumberFormatException e) {
            Toast.makeText(this, "Please enter valid numbers for quantity and price", Toast.LENGTH_SHORT).show();
            return;
        }

        // Validate numeric values
        if (quantity < 0) {
            productQuantityInput.setError("Quantity cannot be negative");
            return;
        }

        if (price < 0) {
            productPriceInput.setError("Price cannot be negative");
            return;
        }

        // Disable button to prevent multiple submissions
        addProductButton.setEnabled(false);
        addProductButton.setText("Adding Product...");

        // Create product data
        Map<String, Object> product = new HashMap<>();
        product.put("name", productName);
        product.put("storeName", storeName);
        product.put("storeAddress", storeAddress.isEmpty() ? "" : storeAddress);
        product.put("description", productDescription);
        product.put("quantity", quantity);
        product.put("price", price);
        product.put("tags", tags.toLowerCase()); // Store tags in lowercase for better searching
        product.put("businessUserId", currentUserId);
        product.put("dateAdded", System.currentTimeMillis());

        // Also add legacy fields for compatibility with existing search
        product.put("category", extractCategoryFromTags(tags));

        // Add to Firestore
        db.collection("products")
                .add(product)
                .addOnSuccessListener(documentReference -> {
                    Log.d("AddProductActivity", "Product added with ID: " + documentReference.getId());
                    Toast.makeText(AddProductActivity.this, "Product added successfully!", Toast.LENGTH_SHORT).show();

                    // Clear form for next product
                    clearForm();

                    // Re-enable button
                    addProductButton.setEnabled(true);
                    addProductButton.setText("Add Product");

                    // Optional: Navigate back to home after success
                    // finish();
                })
                .addOnFailureListener(e -> {
                    Log.w("AddProductActivity", "Error adding product", e);
                    Toast.makeText(AddProductActivity.this, "Error adding product: " + e.getMessage(), Toast.LENGTH_LONG).show();

                    // Re-enable button
                    addProductButton.setEnabled(true);
                    addProductButton.setText("Add Product");
                });
    }

    private boolean validateInputs(String productName, String storeName, String description, String quantity, String price) {
        boolean isValid = true;

        if (TextUtils.isEmpty(productName)) {
            productNameInput.setError("Product name is required");
            isValid = false;
        }

        if (TextUtils.isEmpty(storeName)) {
            storeNameInput.setError("Store name is required");
            isValid = false;
        }

        if (TextUtils.isEmpty(description)) {
            productDescriptionInput.setError("Product description is required");
            isValid = false;
        }

        if (TextUtils.isEmpty(quantity)) {
            productQuantityInput.setError("Quantity is required");
            isValid = false;
        }

        if (TextUtils.isEmpty(price)) {
            productPriceInput.setError("Price is required");
            isValid = false;
        }

        return isValid;
    }

    private String extractCategoryFromTags(String tags) {
        // Simple category extraction from tags for compatibility
        if (tags.toLowerCase().contains("electronic") || tags.toLowerCase().contains("tech")) {
            return "Electronics";
        } else if (tags.toLowerCase().contains("food") || tags.toLowerCase().contains("drink")) {
            return "Food & Drink";
        } else if (tags.toLowerCase().contains("clothing") || tags.toLowerCase().contains("fashion")) {
            return "Fashion";
        } else if (tags.toLowerCase().contains("home") || tags.toLowerCase().contains("furniture")) {
            return "Home";
        } else if (tags.toLowerCase().contains("book") || tags.toLowerCase().contains("education")) {
            return "Education";
        } else if (tags.toLowerCase().contains("sport") || tags.toLowerCase().contains("fitness")) {
            return "Sports";
        } else {
            return "General";
        }
    }

    private void clearForm() {
        productNameInput.setText("");
        storeNameInput.setText("");
        storeAddressInput.setText("");
        productDescriptionInput.setText("");
        productQuantityInput.setText("");
        productTagsInput.setText("");
        productPriceInput.setText("");

        // Clear any error messages
        productNameInput.setError(null);
        storeNameInput.setError(null);
        productDescriptionInput.setError(null);
        productQuantityInput.setError(null);
        productPriceInput.setError(null);
    }
}