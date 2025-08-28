import csv
from io import StringIO
from fastapi.responses import StreamingResponse, JSONResponse
from app.core.enums.enums import FileFormat

from app.schemas.response_models import ResponseModel


class ExportService:
    def export_data(self, data: list[dict], export_format: FileFormat, filename: str):
        if export_format == FileFormat.CSV:
            return self.export_csv(data, filename)
        elif export_format == FileFormat.JSON:
            return self.export_json(data)
        return ResponseModel(status_code=400, message="Invalid export format")

    @staticmethod
    def export_csv(data: list[dict], filename: str):
        csv_file = StringIO()
        if data:
            headers = data[0].keys()
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        csv_file.seek(0)

        return StreamingResponse(
            csv_file,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
        )

    @staticmethod
    def export_json(data: list[dict]):
        return JSONResponse(content=data)


export_service = ExportService()
