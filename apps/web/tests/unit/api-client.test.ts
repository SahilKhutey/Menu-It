import { describe, expect, it } from "vitest";
import { APIClientError } from "../../src/services/api-client";

describe("Web API Client Error", () => {
  it("constructs APIClientError with expected envelope properties", () => {
    const error = new APIClientError(
      "Validation failed",
      422,
      "VALIDATION_ERROR",
      "req-12345",
      [{ field: "email", message: "Invalid email format", code: "INVALID_EMAIL" }]
    );

    expect(error.name).toBe("APIClientError");
    expect(error.message).toBe("Validation failed");
    expect(error.status).toBe(422);
    expect(error.code).toBe("VALIDATION_ERROR");
    expect(error.requestId).toBe("req-12345");
    expect(error.details).toHaveLength(1);
    expect(error.details?.[0].field).toBe("email");
  });
});
