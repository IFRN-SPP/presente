from django.http import HttpResponseForbidden
from django.conf import settings
from django.template import loader
from ipaddress import ip_address, ip_network


class IPRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "IP_RESTRICTION_ENABLED", False)
        self.allowed_networks = getattr(settings, "ALLOWED_IP_NETWORKS", [])
        self.exclude_paths = getattr(settings, "IP_RESTRICTION_EXCLUDE_PATHS", [])

    def __call__(self, request):
        # Skip if IP restriction is disabled
        if not self.enabled:
            return self.get_response(request)

        # Skip if path is excluded
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return self.get_response(request)

        # Get client IP address
        client_ip = self.get_client_ip(request)

        # Check if IP is allowed
        if not self.is_ip_allowed(client_ip):
            # Return 403 Forbidden response
            template = loader.get_template("403_ip_restricted.html")
            context = {"client_ip": client_ip}
            return HttpResponseForbidden(template.render(context, request))

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # X-Forwarded-For can contain multiple IPs, get the first one
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def is_ip_allowed(self, client_ip):
        if not self.allowed_networks:
            # If no networks configured, deny all (safe default)
            return False

        try:
            client_addr = ip_address(client_ip)

            for network in self.allowed_networks:
                try:
                    # Try to match as network (CIDR notation)
                    if "/" in network:
                        if client_addr in ip_network(network, strict=False):
                            return True
                    # Match as individual IP
                    else:
                        if client_addr == ip_address(network):
                            return True
                except ValueError:
                    # Invalid network configuration, skip
                    continue

            return False
        except ValueError:
            # Invalid client IP, deny access
            return False
