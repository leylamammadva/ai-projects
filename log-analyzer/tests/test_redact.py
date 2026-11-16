from analyzer.redact import redact, restore


def test_ips_are_replaced_and_classified():
    out, mapping = redact("from 192.168.1.105 and 8.8.8.8 and 203.0.113.45")
    assert "192.168.1.105" not in out and "8.8.8.8" not in out
    assert "PRIVATE_IP_1" in out and "PUBLIC_IP_1" in out and "PUBLIC_IP_2" in out
    assert mapping["PRIVATE_IP_1"] == "192.168.1.105"


def test_loopback_is_internal():
    out, _ = redact("client 127.0.0.1")
    assert "PRIVATE_IP_1" in out


def test_same_ip_gets_same_token():
    out, _ = redact("fail from 10.0.0.5, fail from 10.0.0.5, fail from 10.0.0.6")
    assert out.count("PRIVATE_IP_1") == 2 and "PRIVATE_IP_2" in out


def test_emails_are_replaced():
    out, mapping = redact("login failed for leyla@example.com")
    assert "leyla@example.com" not in out and mapping["EMAIL_1"] == "leyla@example.com"


def test_invalid_ip_is_left_alone():
    out, mapping = redact("version 999.1.1.1 started")
    assert "999.1.1.1" in out and mapping == {}


def test_text_without_sensitive_data_is_unchanged():
    text = "2024-01-15 08:23:11 INFO Server started successfully"
    assert redact(text) == (text, {})


def test_restore_returns_original_even_with_ten_or_more_tokens():
    original = " ".join(f"10.0.0.{i}" for i in range(1, 13)) + " admin@corp.local"
    out, mapping = redact(original)
    assert "PRIVATE_IP_10" in out
    assert restore(out, mapping) == original
