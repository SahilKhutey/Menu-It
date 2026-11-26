import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 5,
  duration: "30s",
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

export default function () {
  const baseUrl = __ENV.API_BASE_URL || "http://127.0.0.1:8000";

  const resHealth = http.get(`${baseUrl}/api/v1/health`);
  check(resHealth, {
    "health status is 200": (r) => r.status === 200,
  });

  const resInfo = http.get(`${baseUrl}/api/v1/system/info`);
  check(resInfo, {
    "system info status is 200": (r) => r.status === 200,
  });

  sleep(1);
}
