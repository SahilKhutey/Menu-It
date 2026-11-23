/**
 * ModularMenu Canonical OpenAPI 3.1 TypeScript Definitions (ARC-07 §13.3).
 * Generated from FastAPI backend openapi.json.
 */

export interface paths {
  "/api/v1/auth/login": {
    post: {
      requestBody: {
        content: {
          "application/json": {
            email: string;
            password: string;
          };
        };
      };
      responses: {
        200: {
          content: {
            "application/json": {
              access_token: string;
              token_type: string;
              user_id: string;
              email: string;
              full_name: string;
              is_platform_admin?: boolean;
            };
          };
        };
      };
    };
  };
  "/api/v1/auth/register": {
    post: {
      requestBody: {
        content: {
          "application/json": {
            email: string;
            password: string;
            full_name: string;
            organization_name: string;
            restaurant_name: string;
          };
        };
      };
      responses: {
        201: {
          content: {
            "application/json": {
              access_token: string;
              token_type: string;
              user_id: string;
              email: string;
              full_name: string;
            };
          };
        };
      };
    };
  };
  "/api/v1/organizations": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": Array<{
              id: string;
              name: string;
              slug: string;
              status: string;
              country_code: string;
              default_currency: string;
              created_at: string;
              updated_at: string;
            }>;
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          "application/json": {
            name: string;
            slug: string;
            country_code?: string;
            default_currency?: string;
          };
        };
      };
      responses: {
        201: {
          content: {
            "application/json": {
              id: string;
              name: string;
              slug: string;
              status: string;
            };
          };
        };
      };
    };
  };
  "/api/v1/restaurants": {
    get: {
      responses: {
        200: {
          content: {
            "application/json": Array<{
              id: string;
              organization_id: string;
              name: string;
              slug: string;
              status: string;
              currency: string;
              time_zone: string;
            }>;
          };
        };
      };
    };
    post: {
      requestBody: {
        content: {
          "application/json": {
            name: string;
            slug: string;
            currency?: string;
            time_zone?: string;
          };
        };
      };
      responses: {
        201: {
          content: {
            "application/json": {
              id: string;
              organization_id: string;
              name: string;
              slug: string;
            };
          };
        };
      };
    };
  };
  "/api/v1/menus/{menu_id}": {
    get: {
      parameters: {
        path: {
          menu_id: string;
        };
      };
      responses: {
        200: {
          content: {
            "application/json": {
              id: string;
              restaurant_id: string;
              name: string;
              slug: string;
              description?: string;
              status: string;
              sort_order: number;
            };
          };
        };
      };
    };
  };
  "/api/v1/menus/{menu_id}/publish": {
    post: {
      parameters: {
        path: {
          menu_id: string;
        };
        header?: {
          "Idempotency-Key"?: string;
        };
      };
      responses: {
        200: {
          content: {
            "application/json": {
              status: string;
              version_number: number;
              checksum: string;
              published_at: string;
              public_url: string;
            };
          };
        };
      };
    };
  };
  "/api/v1/public/restaurants/{restaurant_slug}/menus/{menu_slug}": {
    get: {
      parameters: {
        path: {
          restaurant_slug: string;
          menu_slug: string;
        };
      };
      responses: {
        200: {
          content: {
            "application/json": {
              status: string;
              restaurant_name: string;
              restaurant_slug: string;
              menu_name: string;
              menu_slug: string;
              version_number: number;
              checksum: string;
              published_at: string;
              data: Record<string, any>;
            };
          };
        };
      };
    };
  };
}
