import { describe, expect, it } from "vitest";
import { APIClientError } from "../../src/services/api-client";

describe("Admin API Client Error", () => {
  it("constructs APIClientError for administrative actions", () => {
    const error = new APIClientError(
      "Permission denied",
      403,
      "FORBIDDEN",
      "req-admin-999"
    );

    expect(error.status).toBe(403);
    expect(error.code).toBe("FORBIDDEN");
    expect(error.requestId).toBe("req-admin-999");
  });
});
