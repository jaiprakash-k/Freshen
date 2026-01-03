"""
Response Utilities
Standardized API response helpers.
"""

from typing import Any, Optional


def success_response(
    data: Any = None,
    message: str = "Success",
    **kwargs
) -> dict:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        message: Success message
        **kwargs: Additional fields to include
    
    Returns:
        Standardized response dictionary
    """
    response = {
        "success": True,
        "message": message,
    }
    
    if data is not None:
        response["data"] = data
    
    response.update(kwargs)
    return response


def error_response(
    message: str,
    error_code: str = "ERROR",
    details: Optional[dict] = None
) -> dict:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_code: Error code string
        details: Additional error details
    
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response


def paginated_response(
    data: list,
    total: int,
    page: int = 1,
    limit: int = 20,
    **kwargs
) -> dict:
    """
    Create a paginated response.
    
    Args:
        data: List of items
        total: Total count of all items
        page: Current page number
        limit: Items per page
        **kwargs: Additional fields
    
    Returns:
        Paginated response dictionary
    """
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    response = {
        "success": True,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }
    }
    
    response.update(kwargs)
    return response
