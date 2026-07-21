import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './button.component.html',
  styleUrls: ['./button.component.scss']
})
export class ButtonComponent {
  @Input() label: string = 'Button';
  @Input() type: 'button' | 'submit' = 'button';
  @Input() variant: 'primary' | 'secondary' | 'danger' | 'outline' = 'primary';
  @Input() disabled: boolean = false;
  @Input() fullWidth: boolean = false;
  @Output() onClick = new EventEmitter<void>();

  handleClick() {
    if (!this.disabled) {
      this.onClick.emit();
    }
  }
}
