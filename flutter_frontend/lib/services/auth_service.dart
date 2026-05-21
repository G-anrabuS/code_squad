import 'package:shared_preferences/shared_preferences.dart';

class AuthService {
  static const _jwtKey = "jwt";
  static const _usernameKey = "username";

  Future<void> saveAuth(String jwt, String username) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_jwtKey, jwt);
    await prefs.setString(_usernameKey, username);
  }

  Future<String?> getJwt() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_jwtKey);
  }

  Future<String?> getUsername() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_usernameKey);
  }

  Future<bool> isLoggedIn() async {
    final jwt = await getJwt();
    return jwt != null && jwt.isNotEmpty;
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
