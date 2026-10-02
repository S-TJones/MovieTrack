export default function RatingInput({ value, onChange, disabled = false }) {
  return (
    <div className="rating-control">
      <label htmlFor="personal-rating">Your rating</label>
      <div className="rating-slider-row">
        <input
          id="personal-rating"
          type="range"
          min="0"
          max="5"
          step="0.5"
          value={value}
          onChange={(event) => onChange(Number(event.target.value))}
          disabled={disabled}
        />
        <output htmlFor="personal-rating">{Number(value).toFixed(1)} / 5</output>
      </div>
    </div>
  );
}