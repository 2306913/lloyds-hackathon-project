package com.example.lloyds_hackathon_prototype;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.FirebaseUser;

public class LoginActivity extends AppCompatActivity {

    // Firebase initialisations
    private FirebaseAuth mAuth;

    // UI Elements
    private EditText loginInput, passwordInput;
    private Button loginButton;

    // Additional:
    private String currentUserId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_login);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        // Initialize Firebase Auth
        mAuth = FirebaseAuth.getInstance();

        // Initialize UI elements
        loginInput = findViewById(R.id.loginInput);
        passwordInput = findViewById(R.id.passwordInput);
        loginButton = findViewById(R.id.loginButton);

        // Set click listener for login button
        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loginUser();
            }
        });

        // Check if user is already logged in
        checkCurrentUser();
    }

    /**
     * Check if user is already authenticated and navigate accordingly
     */
    private void checkCurrentUser() {
        FirebaseUser currentUser = mAuth.getCurrentUser();
        if (currentUser != null) {
            // User is already logged in, go directly to home
            currentUserId = currentUser.getUid();
            navigateToHomeActivity();
        }
    }

    /**
     * Attempts to log a user in to the Degree Calculator to allow progress to Home Screen (Dashboard)
     * Uses existing authentication flow with MFA support
     */
    private void loginUser() {
        // Get input values and trim whitespace to avoid input errors
        String login = loginInput.getText().toString().trim();
        String password = passwordInput.getText().toString().trim();

        // Validate input fields
        if (login.isEmpty() || password.isEmpty()) {
            Toast.makeText(this, "Please enter both login and password", Toast.LENGTH_SHORT).show();
            return;
        }

        // Basic email validation
        if (!android.util.Patterns.EMAIL_ADDRESS.matcher(login).matches()) {
            Toast.makeText(this, "Please enter a valid email address", Toast.LENGTH_SHORT).show();
            return;
        }

        // Password length validation
        if (password.length() < 6) {
            Toast.makeText(this, "Password must be at least 6 characters", Toast.LENGTH_SHORT).show();
            return;
        }

        // Disable button to prevent multiple clicks
        loginButton.setEnabled(false);
        loginButton.setText("Logging in...");

        // Attempt user authentication
        mAuth.signInWithEmailAndPassword(login, password)
                .addOnCompleteListener(this, task -> {
                    // Re-enable button
                    loginButton.setEnabled(true);
                    loginButton.setText("Login");

                    if (task.isSuccessful()) {
                        FirebaseUser user = mAuth.getCurrentUser();

                        if (user != null) {
                            currentUserId = user.getUid();
                            Log.d("LoginActivity", "Login successful for user: " + currentUserId);
                            navigateToHomeActivity();
                        }
                    } else {
                        String errorMessage = "Login Failed";
                        if (task.getException() != null) {
                            errorMessage = "Login Failed: " + task.getException().getMessage();
                        }
                        Toast.makeText(LoginActivity.this, errorMessage, Toast.LENGTH_LONG).show();
                        Log.w("LoginActivity", "Login failed", task.getException());
                    }
                });
    }

    private void navigateToHomeActivity() {
        Toast.makeText(LoginActivity.this, "Login Successful!", Toast.LENGTH_SHORT).show();

        Intent intent = new Intent(LoginActivity.this, HomeActivity.class);
        startActivity(intent);
        finish(); // Obliterates this activity so users can't "go back" here (Which would cause issues)
    }
}