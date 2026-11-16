import AppKit
import Foundation
import QuartzCore

// Flipped NSView so (0,0) is top-left, matching standard macOS screen coordinates
class FlippedView: NSView {
    override var isFlipped: Bool { true }
}

// -------------------------------------------------------------
// MARK: - 1. Target Application Window Border Glow
// -------------------------------------------------------------
class TargetWindowGlow {
    let window: NSWindow
    let glowLayer: CALayer
    let tagField: NSTextField
    let screenHeight: CGFloat
    var currentTargetRect: CGRect = .zero
    var trackedAppName: String?
    private var trackingTimer: DispatchSourceTimer?

    init() {
        let screen = NSScreen.main ?? NSScreen.screens[0]
        self.screenHeight = screen.frame.height

        self.window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 600, height: 400),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        // Kept right above the target application, below the cursor overlay
        self.window.level = NSWindow.Level(Int(CGWindowLevelForKey(.floatingWindow)) - 2)
        self.window.isOpaque = false
        self.window.backgroundColor = .clear
        self.window.ignoresMouseEvents = true
        self.window.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]

        let root = FlippedView(frame: NSRect(x: 0, y: 0, width: 600, height: 400))
        root.wantsLayer = true

        self.glowLayer = CALayer()
        self.glowLayer.frame = root.bounds.insetBy(dx: 4, dy: 4)
        // Neon cyan #40ddbc outer glow border
        self.glowLayer.borderColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.88).cgColor
        self.glowLayer.borderWidth = 3.0
        self.glowLayer.cornerRadius = 14.0
        self.glowLayer.shadowColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        self.glowLayer.shadowRadius = 24.0
        self.glowLayer.shadowOpacity = 0.92
        self.glowLayer.shadowOffset = .zero

        // Ethereal breathing aura pulse
        let pulse = CABasicAnimation(keyPath: "opacity")
        pulse.fromValue = 0.65
        pulse.toValue = 1.0
        pulse.duration = 1.5
        pulse.autoreverses = true
        pulse.repeatCount = .infinity
        self.glowLayer.add(pulse, forKey: "breathing_pulse")

        root.layer?.addSublayer(self.glowLayer)

        // Top Status Pill
        self.tagField = NSTextField(labelWithString: " ⚡ CREWLOOM TARGET · ACTIVE ")
        self.tagField.frame = NSRect(x: 24, y: 0, width: 360, height: 24)
        self.tagField.font = NSFont.monospacedSystemFont(ofSize: 10, weight: .bold)
        self.tagField.textColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0)
        self.tagField.wantsLayer = true
        self.tagField.layer?.backgroundColor = NSColor(red: 0.03, green: 0.07, blue: 0.12, alpha: 0.95).cgColor
        self.tagField.layer?.borderColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.85).cgColor
        self.tagField.layer?.borderWidth = 1.2
        self.tagField.layer?.cornerRadius = 12.0
        self.tagField.alignment = .center

        root.addSubview(self.tagField)
        self.window.contentView = root
    }

    func attachTo(targetRect: CGRect, appName: String) {
        self.currentTargetRect = targetRect
        let padding: CGFloat = 6.0
        let winW = targetRect.width + (padding * 2)
        let winH = targetRect.height + (padding * 2)
        let appKitY = self.screenHeight - targetRect.origin.y - targetRect.height - padding
        let appKitX = targetRect.origin.x - padding

        self.window.setFrame(NSRect(x: appKitX, y: appKitY, width: winW, height: winH), display: true)
        if let root = self.window.contentView {
            root.frame = NSRect(x: 0, y: 0, width: winW, height: winH)
            CATransaction.begin()
            CATransaction.setDisableActions(true)
            self.glowLayer.frame = root.bounds.insetBy(dx: 4, dy: 4)
            CATransaction.commit()
        }
        self.tagField.stringValue = " ⚡ CREWLOOM ACTIVE TARGET: \(appName.uppercased()) "
        self.window.makeKeyAndOrderFront(nil)
    }

    func startTracking(appName: String) {
        self.trackedAppName = appName
        self.updateFrameFromTarget(appName: appName)

        self.trackingTimer?.cancel()
        let timer = DispatchSource.makeTimerSource(queue: .main)
        timer.schedule(deadline: .now() + .milliseconds(250), repeating: .milliseconds(250))
        timer.setEventHandler { [weak self] in
            guard let self = self, let name = self.trackedAppName else { return }
            self.updateFrameFromTarget(appName: name)
        }
        self.trackingTimer = timer
        timer.resume()
    }

    func updateFrameFromTarget(appName: String) {
        if let rect = findWindowRect(appName: appName) {
            if rect != self.currentTargetRect {
                self.attachTo(targetRect: rect, appName: appName)
            }
        }
    }

    func hide() {
        self.trackingTimer?.cancel()
        self.trackingTimer = nil
        self.window.orderOut(nil)
    }
}

// Look up active normal window bounds via CGWindowListCopyWindowInfo
func findWindowRect(appName: String) -> CGRect? {
    let options = CGWindowListOption([.optionOnScreenOnly, .excludeDesktopElements])
    guard let list = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] else {
        return nil
    }

    for win in list {
        let owner = win[kCGWindowOwnerName as String] as? String ?? ""
        let layer = win[kCGWindowLayer as String] as? Int ?? -1

        if owner.localizedCaseInsensitiveContains(appName) && layer == 0 {
            if let boundsDict = win[kCGWindowBounds as String] as? [String: Any],
               let x = boundsDict["X"] as? CGFloat,
               let y = boundsDict["Y"] as? CGFloat,
               let w = boundsDict["Width"] as? CGFloat,
               let h = boundsDict["Height"] as? CGFloat,
               w > 120, h > 120 {
                return CGRect(x: x, y: y, width: w, height: h)
            }
        }
    }
    return nil
}

// -------------------------------------------------------------
// MARK: - 2. Cyber Ghost Cursor with Holographic HUD
// -------------------------------------------------------------
class CyberGhostCursor {
    let window: NSWindow
    let arrowLayer: CAShapeLayer
    let arrowAccentLayer: CAShapeLayer
    let tipDotLayer: CALayer
    let reticleLayer: CAShapeLayer
    let shockwaveLayer: CAShapeLayer
    let badgeView: NSView
    let titleLabel: NSTextField
    let actionLabel: NSTextField
    let telemetryLabel: NSTextField
    let screenHeight: CGFloat

    let tipX: CGFloat = 25.0
    let tipY: CGFloat = 25.0

    var currentX: CGFloat = 200.0
    var currentY: CGFloat = 200.0
    private var glideTimer: DispatchSourceTimer?

    init() {
        let screen = NSScreen.main ?? NSScreen.screens[0]
        self.screenHeight = screen.frame.height

        self.window = NSWindow(
            contentRect: NSRect(x: 100, y: 100, width: 400, height: 140),
            styleMask: [.borderless],
            backing: .buffered,
            defer: false
        )
        self.window.level = .floating
        self.window.isOpaque = false
        self.window.backgroundColor = .clear
        self.window.ignoresMouseEvents = true
        self.window.collectionBehavior = [.canJoinAllSpaces, .stationary, .ignoresCycle]

        let root = FlippedView(frame: NSRect(x: 0, y: 0, width: 400, height: 140))
        root.wantsLayer = true

        // Vector Pointer Arrow (Aerospace Cyber Profile)
        let arrowPath = CGMutablePath()
        arrowPath.move(to: CGPoint(x: tipX, y: tipY))
        arrowPath.addLine(to: CGPoint(x: tipX, y: tipY + 28))
        arrowPath.addLine(to: CGPoint(x: tipX + 7, y: tipY + 22))
        arrowPath.addLine(to: CGPoint(x: tipX + 13, y: tipY + 32))
        arrowPath.addLine(to: CGPoint(x: tipX + 18, y: tipY + 29))
        arrowPath.addLine(to: CGPoint(x: tipX + 12, y: tipY + 19))
        arrowPath.addLine(to: CGPoint(x: tipX + 22, y: tipY + 19))
        arrowPath.closeSubpath()

        self.arrowLayer = CAShapeLayer()
        self.arrowLayer.path = arrowPath
        self.arrowLayer.fillColor = NSColor(red: 0.03, green: 0.07, blue: 0.12, alpha: 0.97).cgColor
        self.arrowLayer.strokeColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        self.arrowLayer.lineWidth = 2.0
        self.arrowLayer.shadowColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        self.arrowLayer.shadowRadius = 14.0
        self.arrowLayer.shadowOpacity = 0.95
        self.arrowLayer.shadowOffset = .zero

        // Interior Neon Accent Line
        let accentPath = CGMutablePath()
        accentPath.move(to: CGPoint(x: tipX + 3, y: tipY + 6))
        accentPath.addLine(to: CGPoint(x: tipX + 3, y: tipY + 20))
        accentPath.addLine(to: CGPoint(x: tipX + 8, y: tipY + 16))

        self.arrowAccentLayer = CAShapeLayer()
        self.arrowAccentLayer.path = accentPath
        self.arrowAccentLayer.strokeColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.9).cgColor
        self.arrowAccentLayer.lineWidth = 1.4
        self.arrowAccentLayer.lineCap = .round

        // Tip Glowing Energy Dot
        self.tipDotLayer = CALayer()
        self.tipDotLayer.frame = CGRect(x: tipX - 2.5, y: tipY - 2.5, width: 5.0, height: 5.0)
        self.tipDotLayer.cornerRadius = 2.5
        self.tipDotLayer.backgroundColor = NSColor.white.cgColor
        self.tipDotLayer.shadowColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        self.tipDotLayer.shadowRadius = 7.0
        self.tipDotLayer.shadowOpacity = 1.0

        // Rotating Targeting Reticle
        let reticleRadius: CGFloat = 16.0
        let reticleRect = CGRect(x: tipX - reticleRadius, y: tipY - reticleRadius, width: reticleRadius * 2, height: reticleRadius * 2)
        let reticlePath = CGPath(ellipseIn: reticleRect, transform: nil)

        self.reticleLayer = CAShapeLayer()
        self.reticleLayer.path = reticlePath
        self.reticleLayer.fillColor = NSColor.clear.cgColor
        self.reticleLayer.strokeColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.8).cgColor
        self.reticleLayer.lineWidth = 1.2
        self.reticleLayer.lineDashPattern = [4, 4]

        let rotateAnim = CABasicAnimation(keyPath: "transform.rotation.z")
        rotateAnim.fromValue = 0.0
        rotateAnim.toValue = Double.pi * 2.0
        rotateAnim.duration = 4.0
        rotateAnim.repeatCount = .infinity
        self.reticleLayer.add(rotateAnim, forKey: "reticle_rotation")

        // Shockwave Ring
        self.shockwaveLayer = CAShapeLayer()
        self.shockwaveLayer.path = reticlePath
        self.shockwaveLayer.fillColor = NSColor.clear.cgColor
        self.shockwaveLayer.strokeColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        self.shockwaveLayer.lineWidth = 2.5
        self.shockwaveLayer.opacity = 0.0

        root.layer?.addSublayer(self.reticleLayer)
        root.layer?.addSublayer(self.arrowLayer)
        root.layer?.addSublayer(self.arrowAccentLayer)
        root.layer?.addSublayer(self.tipDotLayer)
        root.layer?.addSublayer(self.shockwaveLayer)

        // Holographic Glass Card
        self.badgeView = NSView(frame: NSRect(x: 58, y: 15, width: 330, height: 74))
        self.badgeView.wantsLayer = true
        self.badgeView.layer?.backgroundColor = NSColor(red: 0.03, green: 0.07, blue: 0.12, alpha: 0.95).cgColor
        self.badgeView.layer?.borderColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.8).cgColor
        self.badgeView.layer?.borderWidth = 1.5
        self.badgeView.layer?.cornerRadius = 10.0
        self.badgeView.layer?.shadowColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 0.65).cgColor
        self.badgeView.layer?.shadowRadius = 16.0
        self.badgeView.layer?.shadowOpacity = 0.85
        self.badgeView.layer?.shadowOffset = .zero

        // Pulsing status dot
        let dot = NSView(frame: NSRect(x: 12, y: 52, width: 8, height: 8))
        dot.wantsLayer = true
        dot.layer?.cornerRadius = 4.0
        dot.layer?.backgroundColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        dot.layer?.shadowColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0).cgColor
        dot.layer?.shadowRadius = 6.0
        dot.layer?.shadowOpacity = 1.0
        self.badgeView.addSubview(dot)

        self.titleLabel = NSTextField(labelWithString: "CREWLOOM AGENT [VIRTUAL]")
        self.titleLabel.frame = NSRect(x: 26, y: 49, width: 290, height: 16)
        self.titleLabel.font = NSFont.monospacedSystemFont(ofSize: 10, weight: .bold)
        self.titleLabel.textColor = NSColor(red: 0.25, green: 0.87, blue: 0.74, alpha: 1.0)
        self.badgeView.addSubview(self.titleLabel)

        self.actionLabel = NSTextField(labelWithString: "Autonomous Cursor Ready")
        self.actionLabel.frame = NSRect(x: 12, y: 27, width: 305, height: 20)
        self.actionLabel.font = NSFont.systemFont(ofSize: 12, weight: .semibold)
        self.actionLabel.textColor = .white
        self.badgeView.addSubview(self.actionLabel)

        self.telemetryLabel = NSTextField(labelWithString: "POS: 100, 100 · HARDWARE ISOLATED")
        self.telemetryLabel.frame = NSRect(x: 12, y: 8, width: 305, height: 16)
        self.telemetryLabel.font = NSFont.monospacedSystemFont(ofSize: 9, weight: .regular)
        self.telemetryLabel.textColor = NSColor(red: 0.55, green: 0.88, blue: 0.80, alpha: 0.85)
        self.badgeView.addSubview(self.telemetryLabel)

        root.addSubview(self.badgeView)
        self.window.contentView = root
        self.window.makeKeyAndOrderFront(nil)
    }

    func setPosition(screenX: CGFloat, screenY: CGFloat, action: String? = nil) {
        self.currentX = screenX
        self.currentY = screenY

        let appKitTipY = self.screenHeight - screenY
        let winOriginX = screenX - self.tipX
        let winOriginY = appKitTipY - self.window.frame.height + self.tipY

        self.window.setFrameOrigin(NSPoint(x: winOriginX, y: winOriginY))
        if let act = action {
            self.actionLabel.stringValue = act
        }
        self.telemetryLabel.stringValue = "POS: \(Int(screenX)), \(Int(screenY)) · HARDWARE ISOLATED"
    }

    func glideTo(targetX: CGFloat, targetY: CGFloat, durationMs: Double, action: String, completion: (() -> Void)? = nil) {
        self.glideTimer?.cancel()
        self.actionLabel.stringValue = action

        let startX = self.currentX
        let startY = self.currentY
        let startTime = CFAbsoluteTimeGetCurrent()
        let durationSec = max(durationMs / 1000.0, 0.05)

        let timer = DispatchSource.makeTimerSource(queue: .main)
        timer.schedule(deadline: .now(), repeating: .milliseconds(16))

        timer.setEventHandler { [weak self] in
            guard let self = self else { return }
            let elapsed = CFAbsoluteTimeGetCurrent() - startTime
            let rawT = min(elapsed / durationSec, 1.0)

            // Cubic ease-in-out curve
            let t = rawT < 0.5 ? 4.0 * rawT * rawT * rawT : 1.0 - pow(-2.0 * rawT + 2.0, 3.0) / 2.0
            let interX = startX + (targetX - startX) * CGFloat(t)
            let interY = startY + (targetY - startY) * CGFloat(t)

            self.setPosition(screenX: interX, screenY: interY)

            if rawT >= 1.0 {
                self.glideTimer?.cancel()
                self.glideTimer = nil
                self.setPosition(screenX: targetX, screenY: targetY)
                completion?()
            }
        }
        self.glideTimer = timer
        timer.resume()
    }

    func triggerClickShockwave(action: String = "Click! [Focus]") {
        self.actionLabel.stringValue = action
        let group = CAAnimationGroup()
        group.duration = 0.45

        let scale = CABasicAnimation(keyPath: "transform.scale")
        scale.fromValue = 0.4
        scale.toValue = 2.4

        let fade = CABasicAnimation(keyPath: "opacity")
        fade.fromValue = 1.0
        fade.toValue = 0.0

        group.animations = [scale, fade]
        self.shockwaveLayer.add(group, forKey: "shockwave")
    }
}

// -------------------------------------------------------------
// MARK: - Main Application & IPC Command Loop
// -------------------------------------------------------------
let app = NSApplication.shared
let glow = TargetWindowGlow()
let cursor = CyberGhostCursor()

cursor.setPosition(screenX: 200, screenY: 200, action: "Crewloom Agent Initialized")

FileHandle.standardInput.readabilityHandler = { handle in
    let data = handle.availableData
    guard let str = String(data: data, encoding: .utf8), !str.isEmpty else { return }
    let lines = str.components(separatedBy: .newlines)

    for line in lines where !line.isEmpty {
        let parts = line.components(separatedBy: "|")
        let cmd = parts[0]

        DispatchQueue.main.async {
            switch cmd {
            case "GLOW":
                let appName = parts.count > 1 ? parts[1] : "TextEdit"
                glow.startTracking(appName: appName)
            case "GLOW_RECT":
                if parts.count >= 6,
                   let x = Double(parts[1]),
                   let y = Double(parts[2]),
                   let w = Double(parts[3]),
                   let h = Double(parts[4]) {
                    let name = parts.count > 5 ? parts[5] : "Target Window"
                    glow.attachTo(targetRect: CGRect(x: x, y: y, width: w, height: h), appName: name)
                }
            case "GLOW_HIDE":
                glow.hide()
            case "GLIDE":
                if parts.count >= 5,
                   let tx = Double(parts[1]),
                   let ty = Double(parts[2]),
                   let dur = Double(parts[3]) {
                    cursor.glideTo(targetX: CGFloat(tx), targetY: CGFloat(ty), durationMs: dur, action: parts[4])
                }
            case "MOVE":
                if parts.count >= 4,
                   let x = Double(parts[1]),
                   let y = Double(parts[2]) {
                    cursor.setPosition(screenX: CGFloat(x), screenY: CGFloat(y), action: parts[3])
                }
            case "CLICK":
                let act = parts.count > 1 ? parts[1] : "Click! [Focus]"
                cursor.triggerClickShockwave(action: act)
            case "STATUS":
                if parts.count > 1 {
                    cursor.actionLabel.stringValue = parts[1]
                }
            case "QUIT":
                exit(0)
            default:
                break
            }
        }
    }
}

app.run()
