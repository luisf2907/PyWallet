import React, { useState, useEffect, useCallback } from "react";
import { DataGrid, SelectColumn, TextEditor } from "react-data-grid"; // Modified import
import AsyncSelect from "react-select/async";
import { portfolioAPI } from "../../api/portfolioAPI";
import "react-data-grid/lib/styles.css";

// Custom editor for Ticker column with react-select for autocomplete
const TickerEditor = (props) => {
  const { row, onRowChange, ...rest } = props;

  const loadOptions = async (inputValue) => {
    if (!inputValue || inputValue.length < 1) {
      return [];
    }
    try {
      const tickers = await portfolioAPI.searchTickers(inputValue);
      return tickers.map((ticker) => ({ label: ticker.symbol, value: ticker.symbol }));
    } catch (error) {
      console.error("Error fetching tickers:", error);
      return [];
    }
  };

  const handleChange = (selectedOption) => {
    onRowChange({ ...row, ticker: selectedOption ? selectedOption.value : null }, true);
  };

  const currentValue = row.ticker ? { label: row.ticker, value: row.ticker } : null;

  // Styles for react-select to match dark theme
  const selectStyles = {
    container: (provided) => ({ ...provided, width: "100%", height: "100%" }),
    control: (provided, state) => ({
      ...provided,
      height: "100%",
      minHeight: "30px",
      backgroundColor: "var(--input-bg-color, #2d3748)", // Dark background
      borderColor: state.isFocused ? "var(--primary-color, #63b3ed)" : "var(--border-color, #4a5568)", // Border color
      boxShadow: state.isFocused ? `0 0 0 1px var(--primary-color, #63b3ed)` : "none",
      "&:hover": {
        borderColor: "var(--primary-color, #63b3ed)",
      },
    }),
    valueContainer: (provided) => ({ ...provided, height: "100%", padding: "0 8px" }),
    input: (provided) => ({ ...provided, margin: "0px", color: "var(--text-color, #e2e8f0)" }), // Text color for input
    singleValue: (provided) => ({ ...provided, color: "var(--text-color, #e2e8f0)" }), // Text color for selected value
    placeholder: (provided) => ({ ...provided, color: "var(--placeholder-text-color, #a0aec0)" }), // Placeholder text color
    menu: (provided) => ({
      ...provided,
      backgroundColor: "var(--input-bg-color, #2d3748)", // Dark background for dropdown
      zIndex: 9999, // Ensure dropdown is on top
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isFocused ? "var(--primary-color-light, #4299e1)" : "var(--input-bg-color, #2d3748)", // Background for options
      color: state.isSelected ? "var(--text-color-selected, #e2e8f0)" : "var(--text-color, #e2e8f0)", // Text color for options
      "&:hover": {
        backgroundColor: "var(--primary-color-hover, #3182ce)",
      },
    }),
    indicatorSeparator: () => ({ display: "none" }),
    indicatorsContainer: (provided) => ({ ...provided, height: "30px" }),
  };

  return (
    <Select
      {...rest}
      value={currentValue}
      loadOptions={loadOptions}
      onChange={handleChange}
      placeholder="Digite para buscar..."
      isClearable
      cacheOptions
      defaultOptions
      styles={selectStyles}
    />
  );
};

const EditableAssetsTable = ({ portfolioId, onAssetsSubmit }) => {
  const [rows, setRows] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const MIN_EMPTY_ROWS = 10;

  const initialRow = { id: 0, ticker: null, preco_medio: null, quantidade: null, errors: {} };

  const ensureEmptyRows = useCallback((currentRows) => {
    const newRows = [...currentRows];
    let lastFilledRowIndex = -1;
    for (let i = newRows.length - 1; i >= 0; i--) {
      if (newRows[i].ticker || newRows[i].preco_medio || newRows[i].quantidade) {
        lastFilledRowIndex = i;
        break;
      }
    }

    const emptyRowsToAdd = MIN_EMPTY_ROWS - (newRows.length - 1 - lastFilledRowIndex);

    for (let i = 0; i < emptyRowsToAdd; i++) {
      newRows.push({ id: newRows.length > 0 ? newRows[newRows.length - 1].id + 1 : 0, ticker: null, preco_medio: null, quantidade: null, errors: {} });
    }
    // Prune excess empty rows if any, but always keep MIN_EMPTY_ROWS after the last filled one
    if (newRows.length > 0 && lastFilledRowIndex !== -1) {
      const desiredLength = lastFilledRowIndex + 1 + MIN_EMPTY_ROWS;
      if (newRows.length > desiredLength) {
        newRows.splice(desiredLength);
      }
    } else if (lastFilledRowIndex === -1 && newRows.length > MIN_EMPTY_ROWS) {
      // All rows are empty, prune to MIN_EMPTY_ROWS
      newRows.splice(MIN_EMPTY_ROWS);
    }

    return newRows.map((row, index) => ({ ...row, id: index })); // Re-index ids
  }, []);

  useEffect(() => {
    setRows(ensureEmptyRows([initialRow]));
  }, [ensureEmptyRows]);

  const validateCell = async (row, columnKey, value) => {
    let newErrors = { ...row.errors };
    delete newErrors[columnKey]; // Clear previous error for this cell

    if (columnKey === "ticker" && value) {
      try {
        const validation = await portfolioAPI.validateTicker(value);
        if (!validation.exists) {
          newErrors.ticker = "Ticker não encontrado.";
        }
      } catch (err) {
        newErrors.ticker = "Erro ao validar ticker.";
      }
    } else if (columnKey === "preco_medio") {
      if (value !== null && (isNaN(parseFloat(value)) || parseFloat(value) <= 0)) {
        newErrors.preco_medio = "Preço médio inválido.";
      }
    } else if (columnKey === "quantidade") {
      if (value !== null && (isNaN(parseInt(value)) || parseInt(value) <= 0)) {
        newErrors.quantidade = "Quantidade inválida.";
      }
    }
    return newErrors;
  };

  // SIMPLIFIED VERSION FOR TESTING:
  const handleRowsChange = (newRows) => {
    // This is the most basic way to update rows.
    // If textEditor still doesn't work, the issue is likely not in this handler's complexity or async nature.
    setRows(ensureEmptyRows(newRows));
  };

  // Original async version (commented out for testing)
  // const handleRowsChange = async (newRows, { indexes, column }) => {
  //   const rowIndex = indexes[0];
  //   const updatedRow = newRows[rowIndex];
  //   let processedRows = [...newRows];
  //   if (column && (updatedRow[column.key] !== undefined || updatedRow[column.key] === null)) {
  //       const newErrors = await validateCell(updatedRow, column.key, updatedRow[column.key]);
  //       processedRows[rowIndex] = { ...updatedRow, errors: newErrors };
  //   }
  //   setRows(ensureEmptyRows(processedRows));
  // };
  
  const columns = [
    {
      key: "ticker",
      name: "Ticker",
      editor: TickerEditor,
      cellClass: (row) => (row.errors?.ticker ? "cell-error-dark" : null),
      formatter: ({ row }) => (
        <>
          {row.ticker}
          {row.errors?.ticker && <div style={{ color: "var(--error-text-color, #f56565)", fontSize: "0.8em" }}>{row.errors.ticker}</div>}
        </>
      ),
    },
    {
      key: "preco_medio",
      name: "Preço Médio",
      editor: TextEditor,
      cellClass: (row) => (row.errors?.preco_medio ? "cell-error-dark" : null),
      formatter: ({ row }) => (
        <>
          {row.preco_medio}
          {row.errors?.preco_medio && <div style={{ color: "var(--error-text-color, #f56565)", fontSize: "0.8em" }}>{row.errors.preco_medio}</div>}
        </>
      ),
    },
    {
      key: "quantidade",
      name: "Quantidade",
      editor: TextEditor,
      cellClass: (row) => (row.errors?.quantidade ? "cell-error-dark" : null),
      formatter: ({ row }) => (
        <>
          {row.quantidade}
          {row.errors?.quantidade && <div style={{ color: "var(--error-text-color, #f56565)", fontSize: "0.8em" }}>{row.errors.quantidade}</div>}
        </>
      ),
    },
  ];

  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    let allRowsValid = true;
    const assetsToSubmit = [];

    // Perform final validation on all rows before submitting
    const validatedRows = await Promise.all(
      rows.map(async (row) => {
        let currentErrors = { ...row.errors };
        if (row.ticker || row.preco_medio || row.quantidade) {
          // Only validate if row has some data
          if (row.ticker) {
            const tickerErrors = await validateCell(row, "ticker", row.ticker);
            currentErrors = { ...currentErrors, ...tickerErrors };
          } else {
            currentErrors.ticker = "Ticker é obrigatório.";
          }
          const precoErrors = await validateCell(row, "preco_medio", row.preco_medio);
          currentErrors = { ...currentErrors, ...precoErrors };
          if (row.preco_medio === null || row.preco_medio === undefined) {
            // Check if null or undefined
            currentErrors.preco_medio = "Preço médio é obrigatório.";
          }

          const qtdErrors = await validateCell(row, "quantidade", row.quantidade);
          currentErrors = { ...currentErrors, ...qtdErrors };
          if (row.quantidade === null || row.quantidade === undefined) {
            // Check if null or undefined
            currentErrors.quantidade = "Quantidade é obrigatória.";
          }
        }
        return { ...row, errors: currentErrors };
      })
    );

    setRows(ensureEmptyRows(validatedRows)); // Update rows with latest validation errors

    validatedRows.forEach((row) => {
      if (row.ticker && row.preco_medio != null && row.quantidade != null) {
        // Ensure basic fields are present
        if (Object.keys(row.errors).length > 0) {
          allRowsValid = false;
        } else {
          assetsToSubmit.push({
            ticker: row.ticker,
            average_price: parseFloat(row.preco_medio),
            quantity: parseInt(row.quantidade),
            portfolio_id: portfolioId || 1, // Default to 1 if not provided
          });
        }
      }
    });

    if (!allRowsValid) {
      setError("Por favor, corrija os erros na tabela.");
      setIsLoading(false);
      return;
    }

    if (assetsToSubmit.length === 0) {
      setError("Nenhum ativo para adicionar. Preencha a tabela.");
      setIsLoading(false);
      return;
    }

    try {
      const response = await portfolioAPI.submitAssetsBatch(assetsToSubmit);
      console.log("Assets submitted successfully:", response);
      if (onAssetsSubmit) {
        onAssetsSubmit(response);
      }
      // Reset table to initial state after successful submission
      setRows(ensureEmptyRows([{ ...initialRow, id: 0 }]));
      setError(null);
    } catch (err) {
      console.error("Error submitting assets:", err);
      setError(err.message || "Falha ao enviar os ativos. Verifique o console para mais detalhes.");
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleCellClick = (args, event) => {
    console.log("Cell clicked: column=", args.column.key, "rowId=", args.rowId);
  };

  const handleCellDoubleClick = (args, event) => {
    console.log("Cell double-clicked: column=", args.column.key, "rowId=", args.rowId);
  };

  const gridElement = (
    <DataGrid
      columns={columns}
      rows={rows}
      onRowsChange={handleRowsChange} // Using the simplified version
      rowHeight={45}
      className="rdg-dark" // Changed to dark theme
      onCellClick={handleCellClick}             // Added for logging
      onCellDoubleClick={handleCellDoubleClick} // Added for logging
      style={{ 
        height: Math.max(400, rows.length * 45 + 40), 
        minHeight: "200px", 
        resize: "vertical", 
        overflow: "auto",
        border: "1px solid var(--border-color, #4a5568)", // Added border for dark theme
      }} 
    />
  );

  return (
    <div style={{ padding: "20px", color: "var(--text-color, #e2e8f0)" }}> {/* Ensure text color for the container */}
      <style>{/* CSS for error cells and general dark theme adjustments */}
      {`
        /* Define CSS variables if not globally available or for overrides */
        :root {
          --input-bg-color: #2d3748; /* Example dark input background */
          --border-color: #4a5568;   /* Example dark border color */
          --text-color: #e2e8f0;     /* Example dark text color */
          --placeholder-text-color: #a0aec0; /* Example placeholder color */
          --primary-color: #63b3ed; /* Example primary color (blue) */
          --primary-color-light: #4299e1;
          --primary-color-hover: #3182ce;
          --error-text-color: #f56565; /* Example error text color (red) */
          --error-bg-color: #4A2326; /* Darker red for error background */
        }

        .cell-error-dark {
          background-color: var(--error-bg-color, #4A2326) !important;
          color: var(--text-color, #e2e8f0) !important; /* Ensure text is visible on dark error bg */
        }
        .rdg-cell {
            display: flex;
            align-items: center;
            padding: 0 8px;
            background-color: var(--input-bg-color, #2d3748); /* Cell background */
            color: var(--text-color, #e2e8f0); /* Cell text color */
            border-right: 1px solid var(--border-color, #4a5568);
            border-bottom: 1px solid var(--border-color, #4a5568);
        }
        .rdg-header-row .rdg-cell {
            background-color: var(--secondary-color, #1a202c); /* Header background */
            color: var(--text-color, #e2e8f0); /* Header text color */
        }
        .rdg-checkbox-label {
            /* Style for checkboxes if any, to match dark theme */
            border-color: var(--border-color, #4a5568);
        }
        .rdg-checkbox:checked + .rdg-checkbox-label {
            background-color: var(--primary-color, #63b3ed);
        }
      `}
      </style>
      <h3 style={{ marginBottom: "15px", color: "var(--text-color, #e2e8f0)" }}>Adicionar Ativos Manualmente</h3>
      {gridElement}
      {error && <div style={{ color: "var(--error-text-color, #f56565)", marginTop: "10px" }}>{error}</div>}
      <button 
        onClick={handleSubmit} 
        disabled={isLoading}
        style={{
          marginTop: "20px",
          padding: "10px 20px",
          backgroundColor: "var(--primary-color, #007bff)",
          color: "var(--button-text-color, white)", // Use a variable or default to white
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          opacity: isLoading ? 0.7 : 1,
        }}
      >
        {isLoading ? "Enviando..." : "Adicionar Ativos ao Portfólio"}
      </button>
    </div>
  );
};

export default EditableAssetsTable;
