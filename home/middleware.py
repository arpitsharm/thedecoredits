import time
from collections import defaultdict
from django.http import JsonResponse


# In-memory rate limit store
# {ip: [timestamp1, timestamp2, ...]}
_rate_limit_store = defaultdict(list)


class RateLimitMiddleware:
    """
    Simple per-IP rate limiting middleware for KVM 1 CPU protection.
    Tracks requests per IP and blocks excessive traffic.
    """

    # Limits: {url_prefix: (max_requests, window_seconds)}
    LIMITS = {
        '/api/chatbot/': (5, 60),       # 5 requests per minute
        '/review/': (3, 60),            # 3 reviews per minute
        '/submit/': (3, 60),            # 3 quote submits per minute
        '/dashboard/': (30, 60),        # 30 admin requests per minute
    }

    # Global limit for all other paths
    GLOBAL_LIMIT = (60, 60)  # 60 requests per minute

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = self._get_client_ip(request)
        path = request.path
        now = time.time()

        # Check rate limit for matching path
        matched_limit = None
        for prefix, limit in self.LIMITS.items():
            if path.startswith(prefix):
                matched_limit = limit
                break

        if matched_limit is None:
            matched_limit = self.GLOBAL_LIMIT

        max_requests, window = matched_limit

        # Clean old entries
        _rate_limit_store[ip] = [
            t for t in _rate_limit_store[ip]
            if now - t < window
        ]

        # Check limit
        if len(_rate_limit_store[ip]) >= max_requests:
            retry_after = int(window - (now - _rate_limit_store[ip][0]))
            return JsonResponse(
                {'error': 'Too many requests. Try again later.'},
                status=429,
            )

        # Record this request
        _rate_limit_store[ip].append(now)

        # Cleanup periodically (every 100 requests)
        if len(_rate_limit_store) > 1000:
            self._cleanup(now)

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '0.0.0.0')

    def _cleanup(self, now):
        expired_ips = [
            ip for ip, timestamps in _rate_limit_store.items()
            if not timestamps or all(now - t > 120 for t in timestamps)
        ]
        for ip in expired_ips:
            del _rate_limit_store[ip]
