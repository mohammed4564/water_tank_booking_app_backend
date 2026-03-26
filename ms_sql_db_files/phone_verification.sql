USE [WTP_DB]
GO

/****** Object:  Table [dbo].[phone_verifications]    Script Date: 3/26/2026 11:35:55 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[phone_verifications](
	[id] [int] IDENTITY(1,1) NOT NULL,
	[user_id] [int] NOT NULL,
	[otp] [nvarchar](10) NOT NULL,
	[expiry] [datetime] NOT NULL,
	[attempts] [int] NULL,
	[created_at] [datetime] NULL,
	[status] [varchar](20) NULL,
PRIMARY KEY CLUSTERED 
(
	[id] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[phone_verifications] ADD  DEFAULT ('pending') FOR [status]
GO

ALTER TABLE [dbo].[phone_verifications]  WITH CHECK ADD  CONSTRAINT [FK_PhoneVerification_User] FOREIGN KEY([user_id])
REFERENCES [dbo].[users] ([id])
ON DELETE CASCADE
GO

ALTER TABLE [dbo].[phone_verifications] CHECK CONSTRAINT [FK_PhoneVerification_User]
GO


